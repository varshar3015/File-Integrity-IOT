/**
 * ESP32 File Integrity Monitor Alert System
 * 
 * Hardware Alert System for File Integrity Monitor
 * Provides visual (LED) and audio (buzzer) alerts via WiFi
 * 
 * Hardware Connections:
 * - GPIO2:  Green LED (Normal monitoring indicator)
 * - GPIO4:  Red LED (Alert indicator)
 * - GPIO5:  Buzzer (Audio alert)
 * - GND:    Common ground
 * 
 * Author: FIM Project
 * Version: 1.0.0
 * Date: August 8, 2026
 */

#include <WiFi.h>
#include <WebServer.h>

// ============================================================================
// CONFIGURATION - Update these values
// ============================================================================

// WiFi Credentials - IMPORTANT: Change these to your WiFi details!
const char* ssid = "VMR PG 1st floore-3g";      // Your WiFi SSID
const char* password = "8073372230";   // Your WiFi Password

// GPIO Pin Definitions
const int GREEN_LED_PIN = 2;   // Normal operation indicator
const int RED_LED_PIN = 4;     // Alert indicator
const int BUZZER_PIN = 5;      // Audio alert

// Alert Configuration
const int ALERT_DURATION = 5000;    // Red LED stays on for 5 seconds
const int BUZZER_BEEPS = 3;         // Number of buzzer beeps
const int BUZZER_BEEP_DURATION = 200;  // Beep duration in milliseconds
const int BUZZER_PAUSE_DURATION = 200; // Pause between beeps

// Green LED Blink Configuration (Normal Operation)
const int GREEN_BLINK_INTERVAL = 1000;  // Blink every 1 second

// ============================================================================
// GLOBAL VARIABLES
// ============================================================================

WebServer server(80);  // HTTP server on port 80

// State tracking
bool alertActive = false;
unsigned long alertStartTime = 0;
unsigned long lastGreenBlink = 0;
bool greenLedState = false;

// ============================================================================
// SETUP FUNCTION
// ============================================================================

void setup() {
  // Initialize Serial for debugging
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n");
  Serial.println("========================================");
  Serial.println("ESP32 File Integrity Monitor");
  Serial.println("Alert System Starting...");
  Serial.println("========================================");
  
  // Configure GPIO pins
  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  
  // Initial state - all OFF
  digitalWrite(GREEN_LED_PIN, LOW);
  digitalWrite(RED_LED_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);
  
  // Power-on self test
  Serial.println("\nPerforming Power-On Self Test...");
  performSelfTest();
  
  // Connect to WiFi
  connectToWiFi();
  
  // Setup HTTP server routes
  setupServerRoutes();
  
  // Start web server
  server.begin();
  Serial.println("HTTP server started");
  Serial.println("========================================");
  Serial.println("System Ready - Monitoring Mode Active");
  Serial.println("========================================\n");
  
  // Start with green LED on
  digitalWrite(GREEN_LED_PIN, HIGH);
  greenLedState = true;
  lastGreenBlink = millis();
}

// ============================================================================
// MAIN LOOP
// ============================================================================

void loop() {
  // Handle HTTP requests
  server.handleClient();
  
  // Handle alert state
  if (alertActive) {
    handleAlertState();
  } else {
    handleMonitoringState();
  }
}

// ============================================================================
// WIFI CONNECTION
// ============================================================================

void connectToWiFi() {
  Serial.println("\nConnecting to WiFi...");
  Serial.print("SSID: ");
  Serial.println(ssid);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  Serial.println();
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("WiFi Connected Successfully!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Signal Strength: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
    
    // Brief celebration blink
    for (int i = 0; i < 3; i++) {
      digitalWrite(GREEN_LED_PIN, HIGH);
      delay(100);
      digitalWrite(GREEN_LED_PIN, LOW);
      delay(100);
    }
  } else {
    Serial.println("WiFi Connection Failed!");
    Serial.println("Please check credentials and try again.");
    // Error indication - rapid red blinking
    while (true) {
      digitalWrite(RED_LED_PIN, HIGH);
      delay(200);
      digitalWrite(RED_LED_PIN, LOW);
      delay(200);
    }
  }
}

// ============================================================================
// HTTP SERVER ROUTES
// ============================================================================

void setupServerRoutes() {
  // Root endpoint - returns system info
  server.on("/", HTTP_GET, handleRoot);
  
  // Alert endpoint - triggers alert
  server.on("/alert", HTTP_GET, handleAlert);
  
  // Status endpoint - returns current status
  server.on("/status", HTTP_GET, handleStatus);
  
  // 404 handler
  server.onNotFound(handleNotFound);
}

void handleRoot() {
  String html = "<!DOCTYPE html><html><head>";
  html += "<title>ESP32 FIM Alert System</title>";
  html += "<meta name='viewport' content='width=device-width, initial-scale=1'>";
  html += "<style>";
  html += "body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }";
  html += ".container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }";
  html += "h1 { color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }";
  html += ".status { padding: 15px; margin: 15px 0; border-radius: 5px; }";
  html += ".monitoring { background: #d4edda; border-left: 5px solid #28a745; }";
  html += ".alert { background: #f8d7da; border-left: 5px solid #dc3545; }";
  html += ".info { background: #d1ecf1; border: 1px solid #bee5eb; padding: 10px; margin: 10px 0; border-radius: 5px; }";
  html += "button { background: #dc3545; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 5px; cursor: pointer; margin: 10px 5px; }";
  html += "button:hover { background: #c82333; }";
  html += ".endpoints { background: #e7f3ff; padding: 15px; border-radius: 5px; margin-top: 20px; }";
  html += "code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }";
  html += "</style></head><body>";
  html += "<div class='container'>";
  html += "<h1>🔒 ESP32 FIM Alert System</h1>";
  
  if (alertActive) {
    html += "<div class='status alert'>";
    html += "<h2>🚨 ALERT ACTIVE</h2>";
    html += "<p>System is currently in alert state</p>";
    html += "</div>";
  } else {
    html += "<div class='status monitoring'>";
    html += "<h2>✅ Monitoring</h2>";
    html += "<p>System is operating normally</p>";
    html += "</div>";
  }
  
  html += "<div class='info'>";
  html += "<strong>IP Address:</strong> " + WiFi.localIP().toString() + "<br>";
  html += "<strong>Signal Strength:</strong> " + String(WiFi.RSSI()) + " dBm<br>";
  html += "<strong>Uptime:</strong> " + String(millis() / 1000) + " seconds";
  html += "</div>";
  
  html += "<button onclick='fetch(\"/alert\").then(()=>location.reload())'>Trigger Test Alert</button>";
  
  html += "<div class='endpoints'>";
  html += "<h3>API Endpoints</h3>";
  html += "<p><strong>GET /alert</strong> - Trigger security alert</p>";
  html += "<p><strong>GET /status</strong> - Get system status (JSON)</p>";
  html += "<p><strong>GET /</strong> - This page</p>";
  html += "</div>";
  
  html += "</div></body></html>";
  
  server.send(200, "text/html", html);
}

void handleAlert() {
  Serial.println("\n[ALERT] Security alert received from FIM!");
  
  // Activate alert
  alertActive = true;
  alertStartTime = millis();
  
  // Turn off green LED
  digitalWrite(GREEN_LED_PIN, LOW);
  
  // Turn on red LED
  digitalWrite(RED_LED_PIN, HIGH);
  
  // Sound buzzer
  soundBuzzer();
  
  // Send JSON response
  String response = "{\"status\":\"alert_triggered\",\"timestamp\":";
  response += String(millis());
  response += ",\"duration\":";
  response += String(ALERT_DURATION);
  response += "}";
  
  server.send(200, "application/json", response);
  
  Serial.println("[ALERT] Response sent to FIM");
}

void handleStatus() {
  String status = alertActive ? "alert" : "monitoring";
  String response = "{\"status\":\"" + status + "\",";
  response += "\"uptime\":" + String(millis()) + ",";
  response += "\"ip\":\"" + WiFi.localIP().toString() + "\",";
  response += "\"rssi\":" + String(WiFi.RSSI());
  response += "}";
  
  server.send(200, "application/json", response);
}

void handleNotFound() {
  String message = "{\"error\":\"Not Found\",";
  message += "\"uri\":\"" + server.uri() + "\"}";
  server.send(404, "application/json", message);
}

// ============================================================================
// ALERT HANDLING
// ============================================================================

void handleAlertState() {
  unsigned long currentTime = millis();
  
  // Check if alert duration has elapsed
  if (currentTime - alertStartTime >= ALERT_DURATION) {
    // Deactivate alert
    alertActive = false;
    digitalWrite(RED_LED_PIN, LOW);
    
    Serial.println("[SYSTEM] Alert cleared - Returning to monitoring mode");
    
    // Reset green LED blink timing
    lastGreenBlink = currentTime;
    digitalWrite(GREEN_LED_PIN, HIGH);
    greenLedState = true;
  }
}

void handleMonitoringState() {
  unsigned long currentTime = millis();
  
  // Blink green LED
  if (currentTime - lastGreenBlink >= GREEN_BLINK_INTERVAL) {
    greenLedState = !greenLedState;
    digitalWrite(GREEN_LED_PIN, greenLedState ? HIGH : LOW);
    lastGreenBlink = currentTime;
  }
}

void soundBuzzer() {
  // Beep the buzzer specified number of times
  for (int i = 0; i < BUZZER_BEEPS; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(BUZZER_BEEP_DURATION);
    digitalWrite(BUZZER_PIN, LOW);
    
    if (i < BUZZER_BEEPS - 1) {  // Don't delay after last beep
      delay(BUZZER_PAUSE_DURATION);
    }
  }
  
  Serial.print("[BUZZER] Sounded ");
  Serial.print(BUZZER_BEEPS);
  Serial.println(" times");
}

// ============================================================================
// POWER-ON SELF TEST
// ============================================================================

void performSelfTest() {
  Serial.println("Testing Green LED...");
  digitalWrite(GREEN_LED_PIN, HIGH);
  delay(500);
  digitalWrite(GREEN_LED_PIN, LOW);
  delay(300);
  
  Serial.println("Testing Red LED...");
  digitalWrite(RED_LED_PIN, HIGH);
  delay(500);
  digitalWrite(RED_LED_PIN, LOW);
  delay(300);
  
  Serial.println("Testing Buzzer...");
  digitalWrite(BUZZER_PIN, HIGH);
  delay(200);
  digitalWrite(BUZZER_PIN, LOW);
  delay(300);
  
  Serial.println("Self Test Complete - All systems operational\n");
}

// ============================================================================
// END OF CODE
// ============================================================================
