#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Color, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait

# 1. EV3 브릭 및 장치 초기화
ev3 = EV3Brick()

# 알려주신 포트 번호에 맞게 모터와 센서를 정확히 연결합니다.
left_motor = Motor(Port.B)            # 왼쪽 바퀴
right_motor = Motor(Port.C)           # 오른쪽 바퀴
color_sensor = ColorSensor(Port.S3)   # 컬러(색상) 센서
ultrasonic_sensor = UltrasonicSensor(Port.S4) # 초음파 센서

# 로봇 팔 모터 (말씀해주시지 않았지만, 이전에 사용했던 A포트로 유지합니다)
arm_motor = Motor(Port.A)

# 주행 베이스 설정 (바퀴 크기 및 간격)
robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)

# 2. 파란선 따라가기 & 물건 앞 멈춤 로직
DRIVE_SPEED = 100
TURN_RATE = 40
lost_line_count = 0

ev3.speaker.beep() # 출발 알림음

while True:
    # [새로 추가된 기능] 초음파 센서로 물건이 6cm(60mm) 이내로 가까워졌는지 확인
    if ultrasonic_sensor.distance() < 60:
        robot.stop()
        ev3.speaker.beep(frequency=1000, duration=500) # 물건 발견 알림음
        break # 주행을 멈추고 물건 집기 단계로 넘어감

    # 컬러 센서로 파란색 판단 (지그재그 주행)
    current_color = color_sensor.color()
    
    if current_color == Color.BLUE:
        # 파란색 위일 때: 살짝 오른쪽으로 틀면서 전진
        robot.drive(DRIVE_SPEED, TURN_RATE)
        lost_line_count = 0
    else:
        # 파란색이 아닐 때: 살짝 왼쪽으로 틀면서 파란색 찾기
        robot.drive(DRIVE_SPEED, -TURN_RATE)
        lost_line_count += 1
        
    # 물건보다 선이 먼저 끊겼을 경우를 대비한 안전 종료
    if lost_line_count > 100:
        robot.stop()
        break
        
    wait(10) # 0.01초 단위로 빠르게 반복 감지

# 3. 로봇 팔로 물건 집고 오른쪽으로 옮기기
ev3.speaker.play_notes(['C4/4']) # 작업 시작 알림

# 팔을 내려서 물건 집기 (각도는 상황에 맞게 100 숫자를 조절하세요)
arm_motor.run_angle(speed=200, rotation_angle=100, then=Stop.HOLD, wait=True)

# 팔을 올려서 물건 들기
arm_motor.run_angle(speed=200, rotation_angle=-100, then=Stop.HOLD, wait=True)

# 로봇 전체를 오른쪽으로 90도 회전
robot.turn(90)

# 팔을 다시 내려서 물건 내려놓기
arm_motor.run_angle(speed=200, rotation_angle=100, then=Stop.HOLD, wait=True)

# 팔을 원래 위치로 원상복구
arm_motor.run_angle(speed=200, rotation_angle=-100, then=Stop.HOLD, wait=True)

ev3.speaker.play_notes(['G4/4', 'C5/4']) # 모든 작업 완료 알림음