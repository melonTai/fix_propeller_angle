import math
"""
迎角調整板を作るプログラム

xrotor ver 7.55
"""

#=====入力開始=====
board_width = 200
# ねじ穴間の距離[mm]
hole_between = 100
# ねじ穴の高さ[mm]
hole_height = 15
# 水平台における桁の高さ[mm]
beam_height = 165.8
# 回転中心から迎角調整板までの距離[mm]
r = 1050
# ねじ穴直径[mm]
hole = 5

# 桁位置
rib_center = 0.25
# 設計ファイル読み込み(xrotorのrestartfile)
filename = r"bladeDesign2020_ver13"
# サブ翼型のdatファイルパス(ペラ根本、ペラ端で使用)
sub_foil_path = r"sub.dat"
# メイン翼型のdatファイルパス(ペラ中央で使用)
main_foil_path = r"main.dat"
# 出力ファイル名
output_filename = "output.txt"
# 翼型混合比
mix = 0.15
# 規定値から何度迎角を傾けるか[deg]
rot_offset = 0.0

#=====入力終了=====

XDAT_U=[0.0002,0.0003,0.0004,0.0005,0.0006,0.0007,0.0008,0.0009,0.001,0.002,0.003,0.004,0.005,0.006,0.007,0.008,0.009,0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.2, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.3, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.37, 0.38, 0.39, 0.4, 0.41, 0.42, 0.43, 0.44, 0.45, 0.46, 0.47, 0.48, 0.49, 0.5, 0.52, 0.54, 0.56, 0.58, 0.6, 0.62, 0.64, 0.66, 0.68, 0.7, 0.72, 0.74, 0.76, 0.78, 0.8, 0.82, 0.84, 0.86, 0.88, 0.9, 0.92, 0.94, 0.96, 0.98,1.0]

XDAT_D=[1.0, 0.98, 0.96, 0.94, 0.92, 0.9, 0.88, 0.86, 0.84, 0.82, 0.8, 0.78, 0.76, 0.74, 0.72, 0.7, 0.68, 0.66, 0.64, 0.62, 0.6, 0.58, 0.56, 0.54, 0.52, 0.5, 0.49, 0.48, 0.47, 0.46, 0.45, 0.44, 0.43, 0.42, 0.41, 0.4, 0.39, 0.38, 0.37, 0.36, 0.35, 0.34, 0.33, 0.32, 0.31, 0.3, 0.29, 0.28, 0.27, 0.26, 0.25, 0.24, 0.23, 0.22, 0.21, 0.2, 0.19, 0.18, 0.17, 0.16, 0.15, 0.14, 0.13, 0.12, 0.11, 0.1, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.01,0.009,0.008,0.007,0.006,0.005,0.004,0.003,0.002,0.001,0.0009,0.0008,0.0007,0.0006,0.0005,0.0004,0.0003,0.0002, 0.0]

def linear(xs, ys, xn):
    """
        内分する関数(xs昇順)

        Params
        ------
        xs : float list
            翼型のx座標(昇順)
        ys : float list
            翼型のy座標
        xn : float
            内分点

        Returns
        -------
        float
            xnで内分した時のyの値。内分不可の時は、ys[0]。
            また、翼型の前縁または後縁にあたるx座標が、引数に渡されたときは、0
    """
    if(xn == 0.0 or xn == 1.0):
        return 0.0
    for i in range(len(xs)-1):
        if(xs[i] < xn and xn < xs[i+1]):
            return ((xs[i+1] - xn) * ys[i] + (xn - xs[i]) * ys[i+1]) / (xs[i+1] - xs[i])
        if(xs[i] == xn):
            return ys[i]
    print('none data')
    return ys[0]


def linear_reverse(xs, ys, xn):
    """
        内分する関数(xs降順)

        Params
        ------
        xs : float list
            翼型のx座標(降順)
        ys : float list
            翼型のy座標
        xn : float
            内分点

        Returns
        -------
        float
            xnで内分した時のyの値。内分不可の時は、ys[0]。
            また、翼型の前縁または後縁にあたるx座標が、引数に渡されたときは、0
    """
    if(xn == 0.0 or xn == 1.0):
        return 0.0
    for i in range(len(xs)-1):
        if(xs[i] > xn and xn > xs[i+1]):
            #線形補完(内分している)
            return ((xs[i+1] - xn) * ys[i] + (xn - xs[i]) * ys[i+1]) / (xs[i+1] - xs[i])
        if(xs[i] == xn):
            return ys[i]
    print('none data reverse')
    return ys[0]

def shape_dat(datlist):
    """
        翼型の座標位置をXDAT_U、XDAT_Dに揃える関数

        Params
        ------
        datlist : list
            [[x1,y1],[x2,y2],...]

        Returns
        -------
        list
            [[XDAT_D[0],newy[0]],[XDAT_D[1],newy[1]],
            ...,[XDAT_D[-1],newy[m],[XDAT_U[0],newy[m+1]],[XDAT_U[1],newy[m+2]],
            ...,[XDAT_U[-1],newy[-1]]]
    """
    datlist_shaped = []
    datlist_x = [dat[0] for dat in datlist]
    datlist_y = [dat[1] for dat in datlist]
    for x in XDAT_D:

        datlist_shaped.append([x,linear_reverse(datlist_x, datlist_y,x)])
    for x in XDAT_U:
        datlist_shaped.append([x,linear(datlist_x, datlist_y,x)])
    return datlist_shaped

def interpolate_dat(datlist_shaped_list, propotions):
    """
        翼型を混合する関数
        Params
        ------
        datlist_list : float list
            混合する翼型の座標リスト
            shape_datを通すこと
            [
                [   # 翼型1の座標
                    [x11, y11],
                    [x12, y12],
                    ...
                ],
                [   # 翼型2の座標
                    [x21, y21],
                    [x22, y22],
                    ...
                ],
                ...
            ]

        propotions : float list
            各翼型の混合比率(百分率)
            例:
                翼型1:翼型2:翼型3 = 0.2 : 0.3 : 0.5
                で混合するとき引数は
                [0.2, 0.3, 0.5]
            混合比率の合計は1になるよう注意

        Returns
        -------
            float list
            混合した翼型の座標
            [[newx1,newy1],[newx2,newy2],...]
    """
    datlist_new_y = [0]*len(datlist_shaped_list[0])
    datlist_new_x = [dat[0] for dat in datlist_shaped_list[0]]
    for datlist_shaped, p in zip(datlist_shaped_list, propotions):
        datlist_new_y = [dat[1]*p + dat_new_y for dat, dat_new_y in zip(datlist_shaped,datlist_new_y)]
    datlist_new = [[dat_new_x,dat_new_y] for dat_new_x, dat_new_y in zip(datlist_new_x, datlist_new_y)]

    return datlist_new

def getCenterThickness(airfoil, c):#中心線のy座標を求める
    """
    airfoilに与えられた翼型の中心線についてcに与えられたx座標に対応するy座標を得る

    Params
    ------
    airfoil : float list
        翼型の座標
        [[x1,y1],[x2,y2],...]
    c : float
        知りたいx座標(0 < c < 1)
    Returns
    -------
    float
        cに対応するy座標
    """
    p = []
    for i in range(len(airfoil) - 2):
        if (airfoil[i][0] < c and c < airfoil[i+1][0]) or (airfoil[i+1][0] < c and c < airfoil[i][0]):
            m = (c - airfoil[i][0]) / (airfoil[i+1][0] - airfoil[i][0])
            p.append(airfoil[i][1] * (1 - m) + airfoil[i+1][1] * m)
        elif (airfoil[i][0] == c):
            p.append(airfoil[i][1])
    if len(p) == 2:
        return (p[0] + p[1]) / 2.0
    else:
        return 0

if __name__ == '__main__':
    f=open(filename)
    fd = f.read()
    f.close()
    lines = fd.split('\n')
    blade_radius = 1000 * float(lines[5].split()[0]) # 半径を設計ファイルから取得
    print("blade_radius",blade_radius)
    design_data_r = []
    design_data_c = []
    design_data_rot = []
    skip = 9 + int(lines[9].split()[0])*10 + 6
    for line in lines[skip:]:
        d = line.split()
        if(len(d) == 4):
            design_data_r.append(float(d[0]) * blade_radius)
            design_data_c.append(float(d[1]) * blade_radius)
            design_data_rot.append(float(d[2])*math.pi/180)

    f=open(sub_foil_path)
    ad = f.read()
    f.close()
    lines = ad.split('\n')
    _sub_foil = []
    for line in lines[1:]:
        d = line.split()
        if(len(d) == 2):
            _sub_foil.append([float(d[0]), float(d[1])])
    sub_foil = shape_dat(_sub_foil)

    f=open(main_foil_path)
    ad = f.read()
    f.close()
    lines = ad.split('\n')
    _main_foil = []
    for line in lines[1:]:
        d = line.split()
        if(len(d) == 2):
            _main_foil.append([float(d[0]), float(d[1])])
    main_foil = shape_dat(_main_foil)

    output_rib_data = ""

    # 翼弦長
    cmod = linear(design_data_r, design_data_c, r)
    # 水平面を0度としたときのリブの角度をrot_offset分平行移動したもの
    rot = -linear(design_data_r, design_data_rot, r) - rot_offset*math.pi/180

    airfoil_data = []

    airfoil_data = interpolate_dat([sub_foil,main_foil],[mix,1-mix])
    rib_center_camber = getCenterThickness(airfoil_data, rib_center)

    airfoil_poly = []
    rear_airfoil_poly = []

    #桁穴位置を中心に迎角分回転する操作
    for p in airfoil_data:
        px = (p[0] - rib_center) * cmod
        py = (p[1] - rib_center_camber) * cmod
        nx = px * math.cos(rot) - py * math.sin(rot)
        ny = px * math.sin(rot) + py * math.cos(rot)
        airfoil_poly.append([nx, ny])


    rib_front = [(-rib_center * math.cos(rot) + rib_center_camber * math.sin(rot)) * cmod , (-rib_center * math.sin(rot) - rib_center_camber * math.cos(rot)) * cmod]
    rib_end = [((1.0 - rib_center) * math.cos(rot) + rib_center_camber * math.sin(rot)) * cmod , ((1.0 - rib_center) * math.sin(rot) - rib_center_camber * math.cos(rot)) * cmod]

    length = len(airfoil_poly)
    front_index = int(length/2)

    rib_poly = airfoil_poly

    output_rib_data += "BeginPoly;ClosePoly;\n"
    for p in rib_poly[front_index:-2]:
        output_rib_data += "AddPoint(" + str(p[0]) + "," + str(p[1]) + ");\n"
    output_rib_data += "AddPoint(" + str(rib_poly[-1][0]) + "," + str(rib_poly[-1][1]) + ");\n"
    output_rib_data += "AddPoint({},{});\n".format(rib_poly[-1][0] , -beam_height)
    output_rib_data += "AddPoint({},{});\n".format(-board_width/2 , -beam_height)
    output_rib_data += "AddPoint({},{});\n".format(-board_width/2 , rib_poly[front_index][1])
    output_rib_data += "AddPoint({},{});\n".format(rib_poly[front_index][0] , rib_poly[front_index][1])
    output_rib_data += "EndPoly;\n"

    output_rib_data += "Arc(" + str(hole_between/2 - hole / 2) + "," + str(-beam_height + hole_height - hole/2) + "," + str(hole_between/2 + hole / 2) + "," + str(-beam_height + hole_height + hole/2) + ",#0,#360);\n"
    output_rib_data += "Arc(" + str(-hole_between/2 - hole / 2) + "," + str(-beam_height + hole_height - hole/2) + "," + str(-hole_between/2 + hole / 2) + "," + str(-beam_height + hole_height + hole/2) + ",#0,#360);\n"

    #

    with open(output_filename, mode='w') as f:
        f.write(output_rib_data)
