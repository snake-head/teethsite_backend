import math
import tempfile
import os
import base64

import numpy as np
import vtkmodules.all as vtk


def parse_polydata(polydata_string):
    '''
    解析输入的 PolyData 字符串并返回相应的 vtkPolyData 对象。

    :param polydata_string: 包含 PolyData 信息的字符串
    :type polydata_string: str
    :return: 与输入字符串对应的 vtkPolyData 对象
    :rtype: vtkPolyData
    '''
    # 由于 vtkXMLPolyDataReader 期望一个文件，我们需要先将字符串写入一个临时文件
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(polydata_string.encode('utf-8'))
    temp.close()

    # 创建一个 vtkXMLPolyDataReader
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(temp.name)
    reader.Update()

    # 删除临时文件
    os.unlink(temp.name)

    # 从 reader 中获取 polydata
    polydata = reader.GetOutput()

    # 现在你可以使用 polydata 进行进一步的处理
    # ...

    return polydata


def print_point_coordinates(polydata):
    '''
    打印多边形数据中点的坐标信息。

    :param polydata: vtkPolyData对象，包含点信息的多边形数据
    :return: 无返回值
    '''
    points = polydata.GetPoints()
    for i in range(points.GetNumberOfPoints()):
        point = points.GetPoint(i)
        print(f"Point {i}: {point}")


def smooth_polydata(polydata, iterations=200, angle=45):
    '''
    对输入的PolyData进行平滑处理。

    :param polydata: 输入的PolyData数据对象
    :param iterations: 平滑迭代次数，默认为200
    :param angle: 特征边平滑的特征角度（度），默认为180
    :return: 平滑后的PolyData对象
    '''
    smoother = vtk.vtkWindowedSincPolyDataFilter()
    smoother.SetInputData(polydata)

    # 设置平滑参数
    smoother.SetNumberOfIterations(iterations)  # 设置平滑迭代次数
    # smoother.BoundarySmoothingOn()  # 开启边界平滑
    smoother.FeatureEdgeSmoothingOn()  # 开启特征边平滑
    smoother.SetEdgeAngle(angle)  # 设置特征角度
    # smoother.SetPassBand(passBand)  # 设置通带参数

    # 执行平滑滤波
    smoother.Update()

    # 获取平滑后的输出PolyData
    return smoother.GetOutput()


def extract_edge(polydata):
    '''
    从输入的多边形数据中提取边界线。

    :param polydata: vtkPolyData，输入的多边形数据
    :return: vtkPolyData，提取后的边界线数据
    '''
    extract_edges = vtk.vtkFeatureEdges()
    extract_edges.BoundaryEdgesOn()
    extract_edges.FeatureEdgesOff()
    extract_edges.ManifoldEdgesOff()
    extract_edges.NonManifoldEdgesOff()
    # 设置输入数据
    extract_edges.SetInputData(polydata)  # input_poly_data是输入的多边形数据

    # 执行边界线提取
    extract_edges.Update()
    return extract_edges.GetOutput()


def clip_data(port, plane):
    '''
    对给定的3D数据进行剖切操作。

    :param port: vtkAlgorithmOutput
        输入数据端口，表示待剖切的3D数据。
    :param plane: vtkPlane
        剖切平面，用于指定剖切的方向和位置。
    :return: vtkPolyData
        返回剖切后的3D数据，类型为vtkPolyData。
    '''
    clip_polydata = vtk.vtkCutter()
    clip_polydata.SetInputConnection(port)
    clip_polydata.SetCutFunction(plane)
    clip_polydata.GenerateCutScalarsOn()
    clip_polydata.Update()
    return clip_polydata.GetOutput()


def append_data(polydata_list):
    '''
    将多个PolyData对象合并成一个PolyData对象。

    :param polydata_list: 包含多个PolyData对象的列表
    :return: 合并后的PolyData对象
    '''
    append_filter = vtk.vtkAppendPolyData()
    for polydata in polydata_list:
        append_filter.AddInputData(polydata)
    append_filter.Update()
    return append_filter


def display_polydata(polydata_list=None, port_list=None):
    '''
    渲染显示一系列polydata

    :param polydata_list: 包含vtkPolyData对象的列表，用于渲染显示。
    :param port_list: 包含vtkAlgorithmOutput对象的列表，用于渲染显示。
    :return: 无返回值。
    '''
    # 创建渲染器、窗口和交互器
    if port_list is None:
        port_list = []
    if polydata_list is None:
        polydata_list = []
    renderer = vtk.vtkRenderer()

    # 遍历polydata_list中的每个PolyData
    for polydata in polydata_list:
        # 创建映射器，并设置PolyData作为输入
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)

        # 创建表示几何图形的实体
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        # 将表示几何图形的实体添加到渲染器中
        renderer.AddActor(actor)

    for port in port_list:
        # 创建映射器，并设置PolyData作为输入
        mapper = vtk.vtkDataSetMapper()
        try:
            mapper.SetInputConnection(port)
        except Exception as e:
            print(f"Error when setting input connection: {e}")

        # 创建表示几何图形的实体
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        # 将表示几何图形的实体添加到渲染器中
        renderer.AddActor(actor)

    # 开始渲染和交互
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)
    interactor.Initialize()
    render_window.Render()
    interactor.Start()


def translate_polydata(polydata, translate):
    '''
    将给定的PolyData对象按照指定的平移向量进行平移操作。

    :param polydata: vtkPolyData对象，待平移的PolyData数据。
    :param translate: 包含三个浮点数的列表或元组，表示平移的x、y、z分量。
    :return: 平移后的vtkPolyData对象。
    '''
    translation = vtk.vtkTransform()
    translation.Translate(translate)
    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetInputData(polydata)
    transform_filter.SetTransform(translation)
    transform_filter.Update()
    return transform_filter.GetOutput()


def clean_data(data):
    '''
    清理数据函数

    该函数接受一个vtkPolyData对象作为输入，通过vtkCleanPolyData过滤器清理输入数据。

    :param data: vtkPolyData对象，需要进行清理的输入数据。

    :return: vtkCleanPolyData对象，清理后的数据对象。
    '''
    clean_filter = vtk.vtkCleanPolyData()
    clean_filter.SetInputConnection(data.GetOutputPort())
    clean_filter.Update()
    return clean_filter


def clean_single_point_faces(polydata):
    # 创建一个PolyData对象（这里假设你已经有一个PolyData对象）
    polydata_copy = vtk.vtkPolyData()
    polydata_copy.DeepCopy(polydata)  # 创建一个副本以避免原始数据修改

    # 获取面片数据
    faces = polydata_copy.GetPolys()

    # 创建一个点-面片关联的数据结构
    point_face_count = {}  # 用于存储每个点与面片的共享顶点数量

    # 遍历面片数据，统计点与面片的共享顶点数量
    faces.InitTraversal()
    face = vtk.vtkIdList()

    while faces.GetNextCell(face):
        num_points = face.GetNumberOfIds()
        for i in range(num_points):
            point_id = face.GetId(i)
            if point_id not in point_face_count:
                point_face_count[point_id] = 1
            else:
                point_face_count[point_id] += 1

    # 清理只有一个共享顶点的面片
    cells_to_keep = set()

    faces.InitTraversal()
    cell_id = 0

    while faces.GetNextCell(face):
        delete_face = False
        num_points = face.GetNumberOfIds()

        for i in range(num_points):
            point_id = face.GetId(i)
            if point_face_count[point_id] == 1:
                delete_face = True
                break

        if not delete_face:
            cells_to_keep.add(cell_id)

        cell_id += 1

    # 创建一个新的面片数据，只包含要保留的单元
    new_faces = vtk.vtkCellArray()
    faces.InitTraversal()
    cell_id = 0

    while faces.GetNextCell(face):
        if cell_id in cells_to_keep:
            new_faces.InsertNextCell(face)

        cell_id += 1

    # 设置新的面片数据并更新PolyData
    polydata_copy.SetPolys(new_faces)

    return polydata_copy


def select_polydata(polydata, line):
    select_filter = vtk.vtkSelectPolyData()
    select_filter.SetInputData(polydata)
    select_filter.SetLoop(line.GetPoints())
    select_filter.GenerateSelectionScalarsOn()
    select_filter.SetSelectionModeToLargestRegion()
    select_filter.Update()
    clip_filter = vtk.vtkClipPolyData()
    clip_filter.SetInputConnection(select_filter.GetOutputPort())
    clip_filter.Update()
    return clip_filter


def clip_vessel_with_line(vessel, line):
    # 创建vtkImplicitSelectionLoop对象
    implicit_line = vtk.vtkImplicitSelectionLoop()
    implicit_line.SetLoop(line.GetPoints())

    # 使用vtkExtractGeometry来切割vessel
    extract = vtk.vtkExtractGeometry()
    extract.SetInputData(vessel)
    extract.SetImplicitFunction(implicit_line)
    extract.ExtractInsideOn()
    extract.ExtractBoundaryCellsOn()
    extract.Update()

    # 获取切割后的输出
    clipped_vessel = extract.GetOutput()

    return convert_to_polydata(clipped_vessel)


def convert_to_polydata(grid):
    # 创建vtkGeometryFilter以将vtkUnstructuredGrid转换为vtkPolyData
    geometry_filter = vtk.vtkGeometryFilter()
    geometry_filter.SetInputData(grid)
    geometry_filter.Update()

    # 返回转换后的vtkPolyData
    return geometry_filter.GetOutput()

def smooth_line(boundary_line=None):
    if boundary_line is None:
        return

    line_indices = {}  # 用于存储线段的点索引

    if not boundary_line:
        return line_indices

    cells = boundary_line.GetLines()
    cells.InitTraversal()
    id_list = vtk.vtkIdList()

    while cells.GetNextCell(id_list):
        if id_list.GetNumberOfIds() == 2:
            # 提取每个线段的两个点的索引并添加到数组中
            point_index1 = id_list.GetId(0)
            point_index2 = id_list.GetId(1)
            line_indices[str(point_index1)] = point_index2
    points = vtk.vtkPoints()
    last_index = 0
    for i in range(boundary_line.GetNumberOfPoints() + 1):
        point = boundary_line.GetPoint(last_index)
        last_index = line_indices[str(last_index)]
        points.InsertNextPoint(point)

    spline = vtk.vtkParametricSpline()
    spline.SetPoints(points)

    functionSource = vtk.vtkParametricFunctionSource()
    functionSource.SetParametricFunction(spline)
    functionSource.Update()

    splineMapper = vtk.vtkPolyDataMapper()
    splineMapper.SetInputData(functionSource.GetOutput())

    splineActor = vtk.vtkActor()
    splineActor.SetMapper(splineMapper)

    resultPolydata = vtk.vtkPolyData()
    resultPolydata.SetPoints(points)

    resultGlyphFilter = vtk.vtkVertexGlyphFilter()
    resultGlyphFilter.AddInputData(resultPolydata)
    resultGlyphFilter.Update()

    # resultMapper = vtk.vtkPolyDataMapper()
    # resultMapper.SetInputConnection(resultGlyphFilter.GetOutputPort())
    # resultActor = vtk.vtkActor()
    # resultActor.SetMapper(resultMapper)
    # resultActor.GetProperty().SetPointSize(5)  # 设置点的尺寸大小
    # resultActor.GetProperty().SetColor(1, 0.0, 0.0)
    #
    # ren1 = vtk.vtkRenderer()
    # ren1.AddActor(splineActor)
    # ren1.AddActor(resultActor)
    # ren1.SetBackground(0.1, 0.2, 0.4)
    #
    # renWin = vtk.vtkRenderWindow()
    # renWin.AddRenderer(ren1)
    # renWin.SetSize(300, 300)
    #
    # iren = vtk.vtkRenderWindowInteractor()
    # iren.SetRenderWindow(renWin)
    # iren.Initialize()
    # iren.Start()

    return functionSource.GetOutput()


def create_closed_surface(line1, line2):
    # 创建vtkPoints对象
    points = vtk.vtkPoints()

    # 添加line1的点
    for i in range(line1.GetNumberOfPoints()):
        point = line1.GetPoint(i)
        points.InsertNextPoint(point[0], point[1], point[2])

    # 添加line2的点，注意z轴上的位移间隔
    for i in range(line2.GetNumberOfPoints()):
        point = line2.GetPoint(i)
        points.InsertNextPoint(point[0], point[1], point[2])

    # 创建vtkCellArray对象
    triangles = vtk.vtkCellArray()

    # 构造三角形单元
    num_points = line1.GetNumberOfPoints()
    for i in range(num_points):
        triangle1 = vtk.vtkTriangle()
        triangle1.GetPointIds().SetId(0, i % num_points)
        triangle1.GetPointIds().SetId(1, (i + 1) % num_points)
        triangle1.GetPointIds().SetId(2, i % num_points + num_points)

        triangle2 = vtk.vtkTriangle()
        triangle2.GetPointIds().SetId(0, (i + 1) % num_points)
        triangle2.GetPointIds().SetId(1, (i + 1) % num_points + num_points)
        triangle2.GetPointIds().SetId(2, i % num_points + num_points)

        triangles.InsertNextCell(triangle1)
        triangles.InsertNextCell(triangle2)

    # 创建vtkPolyData对象
    side_surface = vtk.vtkPolyData()

    # 将vtkPoints和vtkCellArray与vtkPolyData关联
    side_surface.SetPoints(points)
    side_surface.SetPolys(triangles)

    return side_surface


def create_new_line(line1, line2):
    # 获取line1的点数据
    line1_points = line1.GetPoints()

    # 获取line2的点数据
    line2_points = line2.GetPoints()

    # 获取line1的第一个点作为起始点
    start_point = np.array(line1_points.GetPoint(0))

    # 初始化一个空的新PolyData对象
    line3 = vtk.vtkPolyData()
    points = vtk.vtkPoints()

    # 找到line2中距离start_point最近的点
    min_distance = float('inf')
    nearest_point_index = -1

    for i in range(line2_points.GetNumberOfPoints()):
        point = np.array(line2_points.GetPoint(i))
        distance = np.linalg.norm(point - start_point)

        if distance < min_distance:
            min_distance = distance
            nearest_point_index = i

    if nearest_point_index != -1:
        # 添加nearest_point及其后续点到line3
        for i in range(nearest_point_index,
                       nearest_point_index + line2_points.GetNumberOfPoints()):
            point = line2_points.GetPoint(i % line2_points.GetNumberOfPoints())
            points.InsertNextPoint(point)

        line3.SetPoints(points)

    return line3


def polydata_to_string(polydata):
    '''
    将vtkPolyData对象转换为Base64编码的XML字符串，用于发送给前端。

    :param polydata: vtkPolyData对象，包含要转换的数据。
    :return: Base64编码的XML字符串。
    '''
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetInputData(polydata)
    writer.WriteToOutputStringOn()
    writer.Write()
    xml_string = writer.GetOutputString()
    base64_encoded = base64.b64encode(xml_string.encode()).decode()
    return base64_encoded


def clear_polys_in_line(surface_polydata, line_polydata):
    # 获取表面模型的点和面片数据
    surface_points = surface_polydata.GetPoints()
    surface_polys = surface_polydata.GetPolys()

    # 获取线模型的点数据
    line_points = line_polydata.GetPoints()

    # 创建一个新的vtkPolyData对象来存储结果
    result_polydata = vtk.vtkPolyData()
    result_points = vtk.vtkPoints()
    result_cells = vtk.vtkCellArray()

    result_points = surface_points

    # 创建一个字典来存储线模型中的点的坐标，以便快速查找
    line_points_dict = {}
    for i in range(line_points.GetNumberOfPoints()):
        point = line_points.GetPoint(i)
        line_points_dict[point] = i


    # 提取面片信息
    num_cells = surface_polydata.GetNumberOfCells()

    for i in range(num_cells):
        cell = surface_polydata.GetCell(i)
        points = cell.GetPoints()
        point_ids = cell.GetPointIds()
        poly_contains_only_line_points = True
        for j in range(point_ids.GetNumberOfIds()):
            point_id = point_ids.GetId(j)
            point = points.GetPoint(j)
            # 检查表面模型中的点是否在线模型中
            if point not in line_points_dict:
                poly_contains_only_line_points = False
                break
        if not poly_contains_only_line_points:
            # 如果面片不仅由线模型中的点构成，则将其添加到新的PolyData对象中
            # for j in range(cell_id.GetNumberOfIds()):
            #     point_id = cell_id.GetId(j)
            #     result_points.InsertNextPoint(surface_points.GetPoint(point_id))
            result_cells.InsertNextCell(cell)

    # 将结果点和面片设置给新的PolyData对象
    result_polydata.SetPoints(result_points)
    result_polydata.SetPolys(result_cells)

    return result_polydata


def object_to_list(obj):
    if isinstance(obj, dict):
        # 检查对象是否为字典
        keys = obj.keys()  # 获取对象的所有键，并排序
        return [obj[key] for key in keys]  # 使用列表推导式按照排序后的键顺序创建列表
    else:
        return None  # 如果对象不是字典，返回None或者其他你认为合适的值


def create_vtk_polydata(tooth_point_values, tooth_cell_values):
    # 创建一个空的vtkPoints对象来存储点数据
    points = vtk.vtkPoints()

    # 将一维数组转换为(n, 3)的数组，每行代表一个点的xyz坐标
    num_points = len(tooth_point_values) // 3
    reshaped_points = np.reshape(tooth_point_values, (num_points, 3))

    # 添加点到vtkPoints对象
    for i in range(num_points):
        points.InsertNextPoint(reshaped_points[i])

    # 创建一个空的vtkCellArray对象来存储单元格数据
    cells = vtk.vtkCellArray()

    # 遍历tooth_cell_values数组，每四个一组（一个面片），跳过第一个数字（总是3），后面三个是点索引
    i = 0
    while i < len(tooth_cell_values):
        cells.InsertNextCell(3)  # 指定接下来的单元格由3个点构成
        for j in range(1, 4):  # 跳过每组的第一个数字（3），只添加点索引
            cells.InsertCellPoint(tooth_cell_values[i + j])
        i += 4  # 移动到下一个单元格的开始位置

    # 创建vtkPolyData对象
    polydata = vtk.vtkPolyData()

    # 将点和单元格数据设置到polydata对象
    polydata.SetPoints(points)
    polydata.SetPolys(cells)

    return polydata


def extract_point_and_cell_values(vtk_polydata):
    point_data = vtk_polydata.GetPointData()
    cell_data = vtk_polydata.GetCellData()

    # 提取点数据的值
    point_values = []
    num_points = vtk_polydata.GetNumberOfPoints()
    for i in range(num_points):
        point = vtk_polydata.GetPoint(i)
        point_values.extend(point)

    # 提取单元数据的值
    cell_values = []
    num_cells = vtk_polydata.GetNumberOfCells()
    for i in range(num_cells):
        cell = vtk_polydata.GetCell(i)
        num_points_in_cell = cell.GetNumberOfPoints()
        cell_values.append(num_points_in_cell)
        for j in range(num_points_in_cell):
            cell_values.append(cell.GetPointId(j))

    return point_values, cell_values


if __name__ == '__main__':
    pass
