import numpy as np
import vtkmodules.all as vtk


def vector_projection_length(A, B):
    # 计算A dot B
    dot_product = np.dot(A, B)

    # 计算|B|
    magnitude_B = np.linalg.norm(B)

    # 计算投影长度
    projection_length = dot_product / magnitude_B

    return projection_length




class RootCone:
    def __init__(self, polydata, points_info):
        self.polydata = polydata
        self.resolution = None
        self.circle = None
        self.clip_line = None
        self.cone = None
        self.tooth_name = points_info['toothName']
        self.bottom_sphere_center = points_info['bottomSphereCenter']
        self.top_sphere_center = points_info['topSphereCenter']
        self.radius_sphere_center = points_info['radiusSphereCenter']
        self.up_normal = [0.0, 0.0, 0.0]
        self.origin_up_normal = [0.0, 0.0, 0.0]
        vtk.vtkMath.Subtract(self.top_sphere_center, self.bottom_sphere_center, self.up_normal)
        vtk.vtkMath.Subtract(self.top_sphere_center, self.bottom_sphere_center, self.origin_up_normal)
        vtk.vtkMath.Normalize(self.up_normal)
        radius_normal = [0.0, 0.0, 0.0]
        vtk.vtkMath.Subtract(self.radius_sphere_center, self.bottom_sphere_center, radius_normal)
        self.height = self.calculate_height()
        self.radius = vtk.vtkMath.Normalize(radius_normal)

    def calculate_height(self):
        max_projection_length = float("-inf")  # 初始值为负无穷大
        for i in range(self.polydata.GetNumberOfPoints()):
            point = np.array(self.polydata.GetPoint(i))
            A = point - self.top_sphere_center
            B = [x*-1 for x in self.origin_up_normal]
            projection_length = vector_projection_length(A, B)

            if projection_length > max_projection_length:
                max_projection_length = projection_length
        return max_projection_length + 0.5

    def create_circle(self, resolution):
        '''
        创建一个自定义分辨率的圆，带有三角面片。

        :param resolution: 创建圆时用于确定分辨率的整数值。
        :return: 一个vtkPolyData对象，代表创建的圆。
        '''
        self.resolution = resolution
        # 创建vtkPolyData对象
        circle = vtk.vtkPolyData()
        radius = self.radius
        height = self.height
        center = [
            self.top_sphere_center[0] - height * self.up_normal[0],
            self.top_sphere_center[1] - height * self.up_normal[1],
            self.top_sphere_center[2] - height * self.up_normal[2],
        ]
        direction = self.up_normal
        # 创建圆上的点
        base_points = np.zeros((resolution, 3))
        for i in range(resolution):
            angle = 2 * np.pi * i / resolution
            base_points[i, :] = [radius * np.cos(angle), radius * np.sin(angle), 0]

        # 创建vtkPoints对象
        points = vtk.vtkPoints()
        for point in base_points:
            points.InsertNextPoint(point)

        # 创建vtkCellArray对象，连接圆弧
        lines = vtk.vtkCellArray()
        for i in range(resolution):
            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, i)  # base point
            line.GetPointIds().SetId(1, (i + 1) % resolution)  # tip point
            lines.InsertNextCell(line)

        # 创建vtkCellArray对象，构建三角面片
        # triangles = vtk.vtkCellArray()
        # for i in range(resolution):
        #     triangle = vtk.vtkTriangle()
        #     triangle.GetPointIds().SetId(0, 0)  # center
        #     triangle.GetPointIds().SetId(1, i)  # current point
        #     triangle.GetPointIds().SetId(2, (i + 1) % resolution)  # next point
        #     triangles.InsertNextCell(triangle)

        # 设置圆的点、线和面
        circle.SetPoints(points)
        circle.SetLines(lines)
        # circle.SetPolys(triangles)

        # 创建一个变换对象，用于将圆移动到指定的中心，并朝向指定的方向
        transform = vtk.vtkTransform()
        transform.Translate(center)
        transform.RotateWXYZ(np.degrees(np.arccos(direction[2])), -direction[1], direction[0], 0)
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(transform)
        transformFilter.SetInputData(circle)
        transformFilter.Update()
        self.circle = transformFilter.GetOutput()

        return transformFilter
