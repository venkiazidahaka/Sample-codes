import numpy as np
import math
import struct
import quaternion

# Function performing the calculation


def main(coordinateList, movement_coordinateslist):

    # 直交現在位置
    XYZ = coordinateXYZ(coordinateList)
    RCurrent = rotation_martix(coordinateList)
    current_matrix = inserted_matrix(XYZ, RCurrent)

    # 移動量
    XYZMovement = coordinateXYZ(movement_coordinateslist)
    RMovement = rotation_martix(movement_coordinateslist)

    movement_matrix1 = inserted_matrix(XYZMovement, RMovement)

    result_matrix = return_matrix(current_matrix, movement_matrix1)

    # 移動した後の直交座標
    result_coordinates = return_coordinates(result_matrix)
    # print(" X",result_coordinates[0], "\n",
    #     "Y",result_coordinates[1],"\n",
    #     "Z",result_coordinates[2],"\n",
    #     "A",math.degrees(result_coordinates[3]),"\n",
    #     "B",math.degrees(result_coordinates[4]),"\n",
    #     "C",math.degrees(result_coordinates[5]))

    return result_coordinates


# Rotation Matrix
def rotation_martix(coordinateList):
    A = math.radians(coordinateList[3])
    B = math.radians(coordinateList[4])
    C = math.radians(coordinateList[5])

    return np.array([
        [math.cos(C)*math.cos(B), math.cos(C)*math.sin(B)*math.sin(A) - math.sin(C)
         * math.cos(A), math.cos(C)*math.sin(B)*math.cos(A) + math.sin(C)*math.sin(A)],
        [math.sin(C)*math.cos(B), math.sin(C)*math.sin(B)*math.sin(A) + math.cos(C)
         * math.cos(A), math.sin(C)*math.sin(B)*math.cos(A) - math.cos(C)*math.sin(A)],
        [-1*math.sin(B),                        math.cos(B) *
         math.sin(A),             math.cos(B)*math.cos(A)]
    ])


# 1>Coordinate 4x4 matrix with rotation matrix and coordinate vector
# 2>移動量のCoordinate 4x4 matrix with rotation matrix
def inserted_matrix(XYZ, RCurrent):
    base_line = np.array([0, 0, 0, 1])
    one = np.insert(RCurrent, 3, XYZ, axis=1)
    current_matrix = np.insert(one, 3, base_line, axis=0)

    return current_matrix

# coordinate vector


def coordinateXYZ(coordinateList):
    array = np.array([coordinateList[0], coordinateList[1], coordinateList[2]])

    return array

# multiplying 1> and 2> to get result coordinate matrix


def return_matrix(current_matrix, movement_matrix1):

    return np.dot(current_matrix, movement_matrix1)

# Extracting coordinates from result coordinate matrix


def return_coordinates(return_matrix):
    print("return_matrix", return_matrix)
    X = return_matrix[0][3]
    Y = return_matrix[1][3]
    Z = return_matrix[2][3]
    # A,B,Cの順番を変える禁止　（C->B->A)
    C = math.atan2(return_matrix[1][0], return_matrix[0][0])
    B = math.atan2(-return_matrix[2][0], return_matrix[0]
                   [0]*math.cos(C)+return_matrix[1][0]*math.sin(C))
    A = math.atan2(return_matrix[0][2]*math.sin(C)-return_matrix[1][2]*math.cos(
        C), (-return_matrix[0][1]*math.sin(C)+return_matrix[1][1]*math.cos(C)))

    return np.array([X, Y, Z, A, B, C])


def eulerToquartanion(return_matrix):

    rotation_vector = [return_matrix[3], return_matrix[4], return_matrix[5]]
    quartanion = quaternion.from_rotation_vector(rotation_vector)

    return quartanion


def quartanionToEuler(quartanion):

    eulerRotationVector = quaternion.from_rotation_vector(quartanion)

    return eulerRotationVector


if __name__ == "__main__":
    X = 269.94
    Y = 0.12
    Z = 504.26
    A = math.radians(90)
    B = math.radians(180)
    C = math.radians(60)
    # return_coordinates=main([X,Y,Z,A,B,C],[0,0,0,40,0,0])
    current_coordinates = [X, Y, Z, A, B, C]
    # print(rotation_martix(current_coordinates))
    eulerangles = [A, B, C]
    print("####current_coordinates####")
    print("current_coordinates a", current_coordinates[3])
    print("current_coordinates b", current_coordinates[4])
    print("current_coordinates c", current_coordinates[5])
    # e2q=quaternion.from_euler_angles(eulerangles)

    print("####Euler to quartanion####")
    print(e2q)
    # print("Euler to quartanion　x",e2q[1])
    # print("Euler to quartanion　y",e2q[2])
    # print("Euler to quartanion　z",e2q[3])
    # print("Euler to quartanion　w",e2q[0])
    q2e = quaternion.as_rotation_vector(e2q)
    print("####quartanion to Euler####")
    print(q2e)
    # print("quartanion to Euler a",q2e[0])
    # print("quartanion to Euler b",q2e[1])
    # print("quartanion to Euler c",q2e[2])
    # proper_return_coordinates = np.round(return_coordinates,2)

    # # RCurrent=rotation_martix(A,B,C)
    # # #直交現在位置
    # # XYZ=coordinateXYZ(X,Y,Z)
    # # current_matrix=inserted_matrix(XYZ,RCurrent)

    # # #移動量
    # # RMovement=rotation_martix(0,0,0)
    # # XYZMovement=coordinateXYZ(0,0,20)
    # # movement_matrix1=inserted_matrix(XYZMovement,RMovement)

    # # return_matrix=return_matrix(current_matrix,movement_matrix1)

    # # return_coordinates=return_coordinates(return_matrix)
