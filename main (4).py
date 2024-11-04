import cv2
import mediapipe as mp
import math
import serial
import time

cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence = 0.7, min_tracking_confidence = 0.7)
ser = serial.Serial(f"COM{input('Enter COM port: ')}", baudrate=9600, timeout=50/1000)

fingers = [
    {
        'id': 1,
        'name': 'thumb',
        'len_factor': 0.71,
        'centre_idx': 0,
        'knuckle_idx': 2,
        'tip_idx': 4,
        'start_angle': 0,
        'end_angle': 120
    },
    {
        'id': 2,
        'name': 'pointer',
        'len_factor': 0.79,
        'centre_idx': 0,
        'knuckle_idx': 5,
        'tip_idx': 8,
        'start_angle': 60,
        'end_angle': 140
    },
    {
        'id': 3,
        'name': 'middle',
        'len_factor': 0.88,
        'centre_idx': 0,
        'knuckle_idx': 9,
        'tip_idx': 12,
        'start_angle': 70,
        'end_angle': 160
    },
    {
        'id': 4,
        'name': 'ring',
        'len_factor': 0.88,
        'centre_idx': 0,
        'knuckle_idx': 13,
        'tip_idx': 16,
        'start_angle': 35,
        'end_angle': 130
    },
    {
        'id': 5,
        'name': 'little',
        'len_factor': 0.75,
        'centre_idx': 0,
        'knuckle_idx': 17,
        'tip_idx': 20,
        'start_angle': 55,
        'end_angle': 135
    }
]


def mapRange(val, x1, y1, x2, y2):
    val -= x1
    y1 -= x1

    val /= y1

    val *= (y2 - x2)
    val += x2

    return int(val)


def get_angle(centre, knuckle, tip, len_factor):
    ''' all three coordinates must be vertically aligned '''

    # dist bw centre and knuckle
    d1 = ( (centre[0] - knuckle[0])**2 + (centre[1] - knuckle[1])**2 ) ** 0.5
    # dist bw knuckle and tip
    d2 = abs(tip[1] - knuckle[1])

    length = d1 * len_factor
    if (centre[1] - tip[1]) * (tip[1] - knuckle[1]) > 0:
        angle = 90
    elif d2 / length < 1:
        angle = int(math.acos(d2 / length) * 180 / math.pi)
    else:
        angle = 0
    
    return angle


def align_vertically(centre, knuckle, tip):
    new_knuckle = []
    new_tip = []

    if knuckle[0] == centre[0]:
        return centre[:2], knuckle[:2], tip[:2]

    slope_centre_knuckle = (knuckle[1] - centre[1]) / (knuckle[0] - centre[0])
    m = -1 / slope_centre_knuckle

    dist_centre_knuckle = int(( (centre[0] - knuckle[0])**2 + (centre[1] - knuckle[1])**2 ) ** 0.5)
    new_knuckle = [centre[0], centre[1] - dist_centre_knuckle]

    # d = |ax1 + by1 + c| / (a^2 + b^2) ^ 0.5
    # y = mx => mx - y = 0 => d = |m*x1 - y1| / (1 + m^2) ^ 0.5  {taking centre as origin}
    x_dist = int(abs( slope_centre_knuckle * (tip[0] - centre[0]) - (tip[1] - centre[1])) / (1 + slope_centre_knuckle ** 2) ** 0.5 )
    y_dist = int(abs( m * (tip[0] - centre[0]) - (tip[1] - centre[1])) / (1 + m ** 2) ** 0.5 )

    new_tip = [centre[0] + x_dist, centre[1] - y_dist]

    return centre[:2], new_knuckle, new_tip


while True:
    ret, frame = cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    print_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    results = hands.process(frame)

    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(print_frame, landmarks, mp_hands.HAND_CONNECTIONS)

            coords = [(-1, -1, -1)] * 21

            for idx, landmark in enumerate(landmarks.landmark):
                h, w, c = frame.shape
                cx, cy, cz = int(landmark.x * w), int(landmark.y * h), int(landmark.z * w)

                coords[idx] = (cx, cy, cz)  
            
            angles = [0] * 5
            command = ''

            for finger in fingers:
                centre_idx = finger['centre_idx']
                knuckle_idx = finger['knuckle_idx']
                tip_idx = finger['tip_idx']
                len_factor = finger['len_factor']

                centre, new_knuckle, new_tip = align_vertically(coords[centre_idx], coords[knuckle_idx], coords[tip_idx])

                # cv2.circle(print_frame, centre, 5, (0, 255, 0), 5)
                # cv2.circle(print_frame, new_knuckle, 5, (0, 255, 0), 5)
                # cv2.circle(print_frame, new_tip, 5, (0, 255, 0), 5)

                angle = get_angle(centre, new_knuckle, new_tip, len_factor)
                angle = mapRange(angle, 0, 90, finger['start_angle'], finger['end_angle'])
                angles[finger['id']-1] = angle
                # print(angle)

            for i, angle in enumerate(angles):
                command += f'servo{i+1}:{angle}&'
            ser.write(bytes(command.strip('&'), 'utf-8')) 

    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    cv2.imshow("Camera", print_frame)

    time.sleep(30/1000)


cap.release()
cv2.destroyAllWindows()