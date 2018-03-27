#include <Servo.h>

Servo servo_A;  // create servo object to control a servo
Servo servo_B;

void setup() {
  Serial.begin(9600);
  while (!Serial) {}
  Serial.println("RC>");
  servo_A.attach(3);  
  servo_B.attach(5);
}

void loop() {

  while (Serial.available() > 0) {
    int pwm_delay = Serial.parseInt();
    int pwm_a = Serial.parseInt();
    int pwm_b = Serial.parseInt();
    
    if (Serial.read()=='\r')
    {
      pwm_delay = constrain(pwm_delay, 0, 1000);
      pwm_a = constrain(pwm_a, 0, 180);
      pwm_b = constrain(pwm_b, 0, 180);
      
      int pos_a = servo_A.read();
      int pos_b = servo_B.read();

      while (1)
      {
        if ((Serial.available()>0) || (pos_a==pwm_a && pos_b==pwm_b))
          break;

        if (pos_b < pwm_b)
          pos_b++;
        else if (pos_b > pwm_b)
          pos_b--;
        
        if (pos_a < pwm_a)
          pos_a++;
        else if (pos_a > pwm_a)
          pos_a--;

        servo_A.write(pos_a);
        servo_B.write(pos_b);

        delay(pwm_delay);
      }
    }
  }
}
