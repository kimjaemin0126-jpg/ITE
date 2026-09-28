#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Color, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait

# 1. EV3 브릭 및 장치 초기화
ev3 = EV3Brick()

# 포트 설정 (실제 연결된 포트에 맞게 수정하세요)
left_motor = Motor(Port.B)  # 왼쪽 바퀴
right_motor = Motor(Port.C) # 오른쪽 바퀴
arm_motor = Motor(Port.A)   # 로봇 팔 모터
color_sensor = ColorSensor(Port.S3) # 색상 센서

# 주행 베이스 설정 (바퀴 지름과 두 바퀴 사이의 거리 입력)
robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)

# 2. 파란색 선 따라가기 (커브 주행)
DRIVE_SPEED = 100  # 기본 직진 속도
TURN_RATE = 40     # 회전(커브) 각도 크기
lost_line_count = 0 # 선을 벗어난 횟수를 세는 변수

ev3.speaker.beep() # 시작 알림음

while True:
    current_color = color_sensor.color()
    
    if current_color == Color.BLUE:
        # 파란색 위일 때: 살짝 오른쪽으로 꺾으며 전진 (선의 경계선을 탐색)
        robot.drive(DRIVE_SPEED, TURN_RATE)
        lost_line_count = 0 # 파란색을 찾았으므로 카운트 초기화
        
    else:
        # 파란색을 벗어났을 때: 다시 살짝 왼쪽으로 꺾으며 파란색을 찾음
        robot.drive(DRIVE_SPEED, -TURN_RATE)
        lost_line_count += 1
        
    # 선이 끝난 지점 판단 (파란색을 1초 이상 연속으로 못 찾으면 종료)
    # 지그재그 주행 중 일시적으로 벗어난 것과 선이 완전히 끝난 것을 구분합니다.
    if lost_line_count > 100:
        robot.stop()
        break
        
    wait(10) # 0.01초 대기 후 다시 색상 확인

# 3. 로봇 팔로 물건 집고 오른쪽으로 옮기기
ev3.speaker.play_notes(['C4/4']) # 목표 지점 도달 알림음

# 팔을 내려서 물건 집기
# (각도 100도만큼 회전. 팔이 너무 세게 바닥에 닿으면 각도 값을 줄이세요)
arm_motor.run_angle(speed=200, rotation_angle=100, then=Stop.HOLD, wait=True)

# 팔을 올려서 물건 들기
arm_motor.run_angle(speed=200, rotation_angle=-100, then=Stop.HOLD, wait=True)

# 로봇 전체를 오른쪽으로 90도 회전
robot.turn(90)

# 팔을 다시 내려서 오른쪽 부분에 물건 내려놓기
arm_motor.run_angle(speed=200, rotation_angle=100, then=Stop.HOLD, wait=True)

# 팔을 원래 위치로 원상복구
arm_motor.run_angle(speed=200, rotation_angle=-100, then=Stop.HOLD, wait=True)

ev3.speaker.play_notes(['G4/4', 'C5/4']) # 작업 완료 알림음