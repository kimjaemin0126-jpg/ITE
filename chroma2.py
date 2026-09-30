#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Color, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait

# 1. EV3 브릭 및 장치 초기화
ev3 = EV3Brick()

# 포트 설정 (실제 연결된 포트에 맞게 수정하세요)
left_motor = Motor(Port.B)   # 왼쪽 바퀴
right_motor = Motor(Port.C)  # 오른쪽 바퀴
arm_motor = Motor(Port.A)    # 로봇 팔 모터
color_sensor = ColorSensor(Port.S3)       # 색상 센서 (선 추적용)
ultrasonic_sensor = UltrasonicSensor(Port.S4)  # 초음파 센서 (장애물 감지용)

# 주행 베이스 설정 (바퀴 지름과 두 바퀴 사이의 거리 입력)
robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)

DRIVE_SPEED = 100        # 기본 직진 속도
TURN_RATE = 40           # 회전(커브) 각도 크기 - 클수록 급하게 꺾임
ARM_SPEED = 200          # 팔 모터 속도
ARM_ANGLE = 100          # 팔이 물건을 집기 위해 내려가는 각도
OBSTACLE_DISTANCE = 100  # 장애물로 인식할 거리 (mm). 초음파 센서 기준
LOST_LINE_LIMIT = 100    # 파란색을 이 횟수만큼 연속으로 못 찾으면 선이 끝난 것으로 판단

lost_line_count = 0  # 선을 벗어난(파란색이 아닌) 횟수를 세는 변수

ev3.speaker.beep()  # 시작 알림음

# 2. 파란색 선 따라가기 (지그재그 방식으로 커브 구간도 추적)
#    + 초음파 센서로 전방 장애물 감지
while True:
    distance = ultrasonic_sensor.distance()  # 전방 물체까지의 거리 (mm)

    if distance < OBSTACLE_DISTANCE:
        # 장애물 감지: 즉시 정지하고 경고음을 울리며 대기
        robot.stop()
        ev3.speaker.beep(frequency=1000, duration=150)
        wait(100)
        continue  # 장애물이 사라질 때까지 주행을 재개하지 않음

    current_color = color_sensor.color()

    if current_color == Color.BLUE:
        # 파란색 위일 때: 살짝 오른쪽으로 꺾으며 전진 (선의 경계선을 탐색)
        robot.drive(DRIVE_SPEED, TURN_RATE)
        lost_line_count = 0  # 파란색을 찾았으므로 카운트 초기화
    else:
        # 파란색을 벗어났을 때: 다시 살짝 왼쪽으로 꺾으며 파란색을 찾음
        # 이 지그재그(좌우 반복) 동작 덕분에 선이 휘어져도 경계를 따라 커브를 돌 수 있음
        robot.drive(DRIVE_SPEED, -TURN_RATE)
        lost_line_count += 1

    # 선이 끝난 지점 판단 (파란색을 일정 횟수 이상 연속으로 못 찾으면 종료)
    # 지그재그 주행 중 일시적으로 벗어난 것과 선이 완전히 끝난 것을 구분합니다.
    if lost_line_count > LOST_LINE_LIMIT:
        robot.stop()
        break

    wait(10)  # 0.01초 대기 후 다시 센서 확인

# 3. 로봇 팔로 바로 앞의 물건 집기
ev3.speaker.play_notes(['C4/4'])  # 정지 및 픽업 시작 알림음

# 팔을 내려서 물건 집기
# (각도 100도만큼 회전. 팔이 너무 세게 바닥에 닿으면 ARM_ANGLE 값을 줄이세요)
arm_motor.run_angle(speed=ARM_SPEED, rotation_angle=ARM_ANGLE, then=Stop.HOLD, wait=True)

# 팔을 올려서 물건 들어올리기
arm_motor.run_angle(speed=ARM_SPEED, rotation_angle=-ARM_ANGLE, then=Stop.HOLD, wait=True)

# 4. 로봇을 오른쪽으로 90도 회전시켜 물건을 놓을 위치로 이동
robot.turn(90)

# 팔을 내려서 오른쪽에 물건 내려놓기
arm_motor.run_angle(speed=ARM_SPEED, rotation_angle=ARM_ANGLE, then=Stop.HOLD, wait=True)

# 5. 팔을 원상복구 (물건을 내려놓은 상태에서 원래의 위치로 복귀)
arm_motor.run_angle(speed=ARM_SPEED, rotation_angle=-ARM_ANGLE, then=Stop.HOLD, wait=True)

ev3.speaker.play_notes(['G4/4', 'C5/4'])  # 작업 완료 알림음
