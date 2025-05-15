using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Timers;
using System.Windows.Forms;
using Microsoft.FlightSimulator.SimConnect;

namespace ThrottleBridge
{
    public partial class MainForm : Form
    {
        private SimConnect simConnect = null;
        private Timer reconnectTimer;
        private UdpClient udpClient;
        private const int UDP_PORT = 49005;

        public enum DEFINITIONS { ThrottleSet }
        public enum DATA_REQUESTS { None }

        struct ThrottleData { public double THROTTLE_SET; }

        public MainForm()
        {
            InitializeComponent();
            InitSimConnect();
            InitUDP();
            SetupReconnectTimer();
        }

        private void InitSimConnect()
        {
            try
            {
                simConnect = new SimConnect("ThrottleBridge", Handle, 0, null, 0);
                simConnect.AddToDataDefinition(DEFINITIONS.ThrottleSet, "GENERAL ENG THROTTLE LEVER POSITION:1", "percent", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
                simConnect.RegisterDataDefineStruct<ThrottleData>(DEFINITIONS.ThrottleSet);
                Log("Connected to MSFS");
            }
            catch
            {
                simConnect = null;
                Log("SimConnect not available – will retry.");
            }
        }

        private void InitUDP()
        {
            udpClient = new UdpClient(UDP_PORT);
            udpClient.BeginReceive(OnUDPReceive, null);
        }

        private void OnUDPReceive(IAsyncResult ar)
        {
            IPEndPoint ep = new IPEndPoint(IPAddress.Any, UDP_PORT);
            byte[] data = udpClient.EndReceive(ar, ref ep);

            try
            {
                string text = Encoding.ASCII.GetString(data);
                if (double.TryParse(text, out double value))
                {
                    Invoke((Action)(() => UpdateThrottle(value)));
                }
            }
            catch (Exception ex)
            {
                Log("UDP Error: " + ex.Message);
            }

            udpClient.BeginReceive(OnUDPReceive, null);
        }

        private void UpdateThrottle(double percent)
        {
            labelThrottle.Text = $"Throttle: {(percent * 100):0.0}%";

            if (simConnect != null)
            {
                ThrottleData data = new ThrottleData { THROTTLE_SET = percent * 100.0 };
                simConnect.SetDataOnSimObject(DEFINITIONS.ThrottleSet, SimConnect.SIMCONNECT_OBJECT_ID_USER, SIMCONNECT_DATA_SET_FLAG.DEFAULT, data);
            }
        }

        private void SetupReconnectTimer()
        {
            reconnectTimer = new Timer(3000);
            reconnectTimer.Elapsed += (s, e) =>
            {
                if (simConnect == null)
                    InitSimConnect();
            };
            reconnectTimer.Start();
        }

        private void Log(string message)
        {
            listBoxLog.Items.Add($"{DateTime.Now:T} - {message}");
        }

        protected override void DefWndProc(ref Message m)
        {
            if (simConnect != null)
                simConnect.ReceiveMessage();
            base.DefWndProc(ref m);
        }
    }
}