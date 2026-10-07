import sys
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait

ev3 = EV3Brick()

# 포트 설정 (실제 연결된 포트에 맞게 수정하세요)
left_motor = Motor(Port.B)   # 왼쪽 바퀴
right_motor = Motor(Port.C)  # 오른쪽 바퀴
arm_motor = Motor(Port.A)    # 로봇 팔 모터
blue_sensor = ColorSensor(Port.S3)        # 파란 선 추적용 색상 센서
red_sensor = ColorSensor(Port.S2)         # 빨간 선 추적용 색상 센서 (차체 뒤쪽에 장착, 포트 확인!)
ultrasonic_sensor = UltrasonicSensor(Port.S4)  # 초음파 센서 (장애물 감지용)

# 주행 베이스 설정 (바퀴 지름과 두 바퀴 사이의 거리 입력)
robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)

DRIVE_SPEED = 100        # 기본 직진 속도
TURN_RATE = 40           # 회전(커브) 각도 크기 - 클수록 급하게 꺾임
# 후진(빨간 선, 뒤쪽 센서) 주행 시 꺾는 방향. 뒤쪽 센서는 방향 보정이 앞쪽과 반대라 기본 -1.
# 후진하면서 빨간 선에서 점점 멀어지면(선을 못 따라가면) 이 값을 1로 바꿔 보세요.
REVERSE_STEER_SIGN = -1
ARM_SPEED = 200          # 팔 모터 속도
ARM_ANGLE = 100          # 팔이 물건을 집기 위해 내려가는 각도
# 장애물로 인식할 거리 (mm). 선 끝에 있는 물건보다 "작게" 잡아야 끝 표시 색까지 갈 수 있음
OBSTACLE_DISTANCE = 100

LOST_LINE_LIMIT = 50     # 선 색을 이 횟수만큼 연속으로 못 찾으면 좌우 탐색 시작 (1회 ≈ 0.01초)

# 좌우 탐색 설정: 제자리에서 좌우로 점점 넓게 훑으며 선을 찾음
SEARCH_TURN_RATE = 40    # 탐색할 때 제자리 회전 속도 (도/초)
SEARCH_STEP_ANGLE = 20   # 한 단계마다 넓어지는 각도 (도)
SEARCH_STEPS = 4         # 단계 수. 최대 탐색 각도 = 20 x 4 = 좌우 80도

# ============================================================
# ★★★ 색 인식 값은 여기에 직접 입력하세요 ★★★
# ------------------------------------------------------------
# 입력 방법
#   1) 아래 TUNING_MODE를 True로 바꾸고 EV3에 올려 실행합니다.
#      (주행하지 않고 화면에 두 센서의 (R, G, B) 값이 계속 표시됩니다. 각 값은 0~100)
#   2) 주행할 때와 같은 높이로 센서를 빨간 선 / 파란 선 / 끝 표시(노랑) / 바닥 위에 대고
#      값을 메모합니다.
#   3) 메모한 값을 보고 아래 숫자들을 직접 고쳐 적습니다.
#   4) TUNING_MODE를 False로 되돌리고 다시 올리면 그 값으로 고정되어 주행합니다.
#   ※ 조명이 바뀌는 장소로 가면 1)부터 다시 하세요.
# ------------------------------------------------------------
# [빨간 선 판정]  빨간 선 위에서 읽은 값을 기준으로 적으세요.
RED_MIN = 25      # 빨간 선 위에서 R 값의 최솟값보다 약간 낮게 (바닥 R보다는 높게)
RED_RATIO = 2.0   # R이 G, B보다 몇 배 커야 빨강인지 (바닥은 약 1배, 선 위는 더 큼)

# [파란 선 판정]  파란 선 위에서 읽은 값을 기준으로 적으세요.
BLUE_MIN = 20       # 파란 선 위에서 B 값의 최솟값보다 약간 낮게
BLUE_RATIO = 1.5    # B가 R보다 몇 배 커야 파랑인지
BLUE_G_RATIO = 1.1  # B가 G보다 몇 배 커야 파랑인지

# [선 끝 표시 색(노랑) 판정]  선 끝에 붙여 둔 노랑 표시 위에서 읽은 값을 기준으로 적으세요.
# 파란 선 끝, 빨간 선 끝 모두 이 노랑 표시로 "끝"을 판정합니다.
# 노랑은 R과 G가 높고 B가 낮은 색입니다. (빨강은 G도 낮아서 노랑과 구분됩니다)
YELLOW_MIN = 30     # 노랑 표시 위에서 R, G 값의 최솟값보다 약간 낮게
YELLOW_RATIO = 2.0  # R과 G가 B보다 몇 배 커야 노랑인지
YELLOW_RG_RATIO = 2.0  # R과 G가 서로 몇 배 이내여야 노랑인지 (R만 크면 빨강, G만 크면 초록)

TUNING_MODE = False  # True: 값 측정 모드(주행 안 함) / False: 정상 주행
# ============================================================


def is_red(sensor):
    r, g, b = sensor.rgb()
    return r >= RED_MIN and r > g * RED_RATIO and r > b * RED_RATIO


def is_blue(sensor):
    r, g, b = sensor.rgb()
    return b >= BLUE_MIN and b > r * BLUE_RATIO and b > g * BLUE_G_RATIO


def is_yellow(sensor):
    r, g, b = sensor.rgb()
    return (r >= YELLOW_MIN and g >= YELLOW_MIN
            and r > b * YELLOW_RATIO and g > b * YELLOW_RATIO
            and r < g * YELLOW_RG_RATIO and g < r * YELLOW_RG_RATIO)


def turn_until(target_angle, sensor, is_line, is_end):
    """제자리에서 target_angle(로봇 기준 각도)까지 돌며 선/끝 표시를 찾음.
    찾으면 멈추고 True, 끝까지 못 찾으면 False."""
    direction = 1 if target_angle > robot.angle() else -1  # +: 오른쪽, -: 왼쪽
    robot.drive(0, direction * SEARCH_TURN_RATE)
    while (robot.angle() < target_angle) if direction == 1 else (robot.angle() > target_angle):
        if is_line(sensor) or is_end(sensor):
            robot.stop()
            return True
        wait(10)
    robot.stop()
    return False


def search_line(sensor, is_line, is_end):
    """선을 놓쳤을 때 좌우로 점점 넓게 훑으며 선(또는 끝 표시)을 찾음. 찾으면 True."""
    robot.stop()
    center = robot.angle()
    for step in range(1, SEARCH_STEPS + 1):
        width = SEARCH_STEP_ANGLE * step
        if turn_until(center + width, sensor, is_line, is_end):
            return True
        if turn_until(center - width, sensor, is_line, is_end):
            return True
    return False


def follow_line(sensor, is_line, is_end, reverse=False):
    """sensor로 선을 따라가다가 끝 표시 색(is_end)을 만나면 정지하고 True.
    선을 놓친 뒤 좌우 탐색에도 못 찾으면 정지하고 False.
    reverse=True면 후진하며 따라감 (뒤쪽에 달린 센서용)."""
    lost_line_count = 0  # 선을 벗어난 횟수
    speed = -DRIVE_SPEED if reverse else DRIVE_SPEED
    steer = TURN_RATE * REVERSE_STEER_SIGN if reverse else TURN_RATE

    while True:
        # 장애물 감지: 정지하고 경고음을 울리며 대기 (사라지면 재개)
        # 초음파 센서는 앞쪽을 보므로 후진 중에는 확인하지 않음
        if not reverse and ultrasonic_sensor.distance() < OBSTACLE_DISTANCE:
            robot.stop()
            ev3.speaker.beep(frequency=1000, duration=150)
            wait(100)
            continue

        # 끝 표시 색을 만나면 선의 끝에 도착한 것
        if is_end(sensor):
            robot.stop()
            return True

        if is_line(sensor):
            # 선 위: 살짝 오른쪽으로 꺾으며 전진 (선의 경계선을 탐색)
            robot.drive(speed, steer)
            lost_line_count = 0
        else:
            # 선 벗어남: 살짝 왼쪽으로 꺾으며 선을 다시 찾음
            robot.drive(speed, -steer)
            lost_line_count += 1

        # 일정 횟수 이상 선을 못 찾으면 좌우로 훑으며 탐색
        if lost_line_count > LOST_LINE_LIMIT:
            if search_line(sensor, is_line, is_end):
                lost_line_count = 0  # 찾았으니 다시 주행
            else:
                robot.stop()
                return False  # 끝 표시도 선도 못 찾음 (길을 완전히 잃음)

        wait(10)


def abort_lost():
    """길을 완전히 잃었을 때: 경고음 후 프로그램 종료 (물건 집기 등 이후 동작은 하지 않음)."""
    robot.stop()
    for _ in range(3):
        ev3.speaker.beep(frequency=300, duration=300)
        wait(100)
    sys.exit()


if TUNING_MODE:
    while True:
        ev3.screen.clear()
        ev3.screen.print("Blue S3", blue_sensor.rgb())
        ev3.screen.print("Red  S2", red_sensor.rgb())
        wait(200)

ev3.speaker.beep()  # 시작 알림음

# 2. 파란색 선 따라가기 (노랑 끝 표시를 만나면 정지)
if not follow_line(blue_sensor, is_blue, is_yellow):
    abort_lost()

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

# 6. 팔 원상복구까지 끝났으므로 이제부터 뒤쪽 빨간 센서로 빨간 선을 인식해 후진하며 따라감
ev3.speaker.play_notes(['E4/4', 'G4/4'])  # 빨간 선 추적 시작 알림음
if not follow_line(red_sensor, is_red, is_yellow, reverse=True):
    abort_lost()

ev3.speaker.play_notes(['G4/4', 'C5/4'])  # 작업 완료 알림음