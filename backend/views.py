import copy
import numpy as np
import base64

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from backend.utils import parse_polydata, extract_edge, smooth_polydata, \
    translate_polydata, append_data, clean_data, polydata_to_string, \
    display_polydata, select_polydata, smooth_line, create_closed_surface, \
    create_new_line, clean_single_point_faces
from backend.root import RootCone

import vtkmodules.all as vtk


@csrf_exempt
def generate_root(request):
    if request.method == 'POST':
        # 前端会将牙齿的polydata和牙根的各个坐标数据封装成一个二进制数据，分别解析
        polydata_as_string = request.FILES['polyData'].read().decode('utf-8')
        polydata = parse_polydata(polydata_as_string)
        json_part = json.loads(request.FILES['jsonPart'].read().decode('utf-8'))
        root_cone = RootCone(json_part)
        # 在牙齿上方构造一个圆，作为牙根的根部，该圆的分辨率需要与牙齿的边界对应，便于后续构造封闭图形
        # root_cone.create_circle(resolution=extract_edge(polydata).GetNumberOfPoints())
        # print_point_coordinates(polydata)
        # 平滑
        smoothed_polydata = smooth_polydata(polydata)
        smoothed_polydata = clean_single_point_faces(smoothed_polydata)
        # 提取牙齿边界
        boundary_line = vtk.vtkPolyData()
        boundary_line.DeepCopy(extract_edge(smoothed_polydata))
        smoothed_line = vtk.vtkPolyData()
        smoothed_line.DeepCopy(smooth_line(boundary_line))
        root_cone.create_circle(
            resolution=smoothed_line.GetNumberOfPoints())
        # 平移量，沿牙根方向
        translate = copy.deepcopy(root_cone.up_normal)
        vtk.vtkMath.MultiplyScalar(translate, -1)
        # 将边界线向牙根方向平移一段距离
        translate_edge = translate_polydata(smoothed_line, translate)
        closed_surface = create_closed_surface(smoothed_line, translate_edge)

        clip_line = root_cone.circle
        modified_circle = create_new_line(translate_edge, clip_line)
        closed_surface2 = create_closed_surface(modified_circle, translate_edge)
        # 将牙齿、平移后的边界线、上方圆合并为一个polydata
        append_result = append_data([closed_surface, closed_surface2, root_cone.circle])
        # smoothed_result = smooth_polydata(append_result.GetOutput())
        # 清洗
        # clean_result = clean_data(append_result)
        # 三角剖分算法，将一组三维点转换成一个三角网格
        # delaunay = vtk.vtkDelaunay3D()
        # delaunay.SetInputConnection(clean_result.GetOutputPort())
        # 将输入的数据集（如三维模型或数据）转换为一个几何对象
        # surface_filter = vtk.vtkGeometryFilter()
        # surface_filter.SetInputConnection(delaunay.GetOutputPort())
        # surface_filter.Update()
        # vessel_polydata = surface_filter.GetOutput()
        # display_polydata([root_cone.circle], [])

        # append_filter = vtkAppendPolyData()
        # origin_up_normal = root_cone.origin_up_normal
        # for i in range(3):
        #     plane_point = [0.0, 0.0, 0.0]
        #     plane_point[0] = root_cone.top_sphere_center[0] - i * 0.5 * origin_up_normal[0]
        #     plane_point[1] = root_cone.top_sphere_center[1] - i * 0.5 * origin_up_normal[1]
        #     plane_point[2] = root_cone.top_sphere_center[2] - i * 0.5 * origin_up_normal[2]
        #     plane = vtkPlane()
        #     plane.SetOrigin(plane_point)
        #     plane.SetNormal(root_cone.up_normal)
        #     clip_filter = vtkCutter()
        #     clip_filter.SetInputData(vessel_polydata)
        #     clip_filter.SetCutFunction(plane)
        #     clip_filter.GenerateCutScalarsOn()
        #     clip_filter.Update()
        #     append_filter.AddInputData(clip_filter.GetOutput())
        #     append_filter.Update()
        #
        # append_filter.AddInputData(extract_edge(smoothed_polydata))
        # clean_filter = clean_data(append_filter)
        # delaunay2 = vtkDelaunay3D()
        # delaunay2.SetInputConnection(clean_filter.GetOutputPort())
        # surface_filter2 = vtkGeometryFilter()
        # surface_filter2.SetInputConnection(delaunay2.GetOutputPort())
        # surface_filter2.Update()
        # vessel_polydata2 = surface_filter2.GetOutput()

        # select_filter = select_polydata(vessel_polydata, smoothed_line)
        # display_polydata([], [select_filter.GetOutputPort()])
        #发送给前端
        polydata_string = polydata_to_string(append_result.GetOutput())
        # polydata_string = polydata_to_string(select_filter.GetOutput())
        return JsonResponse({'message': '成功接收数据', 'polydata': polydata_string})

    else:
        return JsonResponse({'message': '请求方法不正确'}, status=400)
