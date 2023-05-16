from django.shortcuts import render
from django.http import JsonResponse
import vtk


def process_polydata(request):
    # 获取前端发送的polydata数据
    polydata = request.POST.get('polydata')

    # 使用vtk库处理polydata数据
    # 注意：这里只是一个示例，具体的处理代码需要根据实际情况编写
    reader = vtk.vtkPolyDataReader()
    reader.SetInputString(polydata)
    reader.Update()

    # 获取处理后的数据
    output = reader.GetOutput()

    # 将处理后的数据发送回前端
    return JsonResponse({'output': output})
