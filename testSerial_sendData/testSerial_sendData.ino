int val = 0;

void setup() {
  Serial1.begin(9600); // ใช้ Serial1 = TX1/RX1 (pin 18/19)
}

void loop() {
  for (int i = 0; i < 100; i++) {
    val = i;
    Serial1.println(val); // ส่งผ่าน Serial1
    delay(50);
  }
  for (int i = 100; i > 0; i--) {
    val = i;
    Serial1.println(val);
    delay(50);
  }
}