#include <cmath>
#include <iostream>
#include <pcl/filters/passthrough.h>
#include <pcl/filters/statistical_outlier_removal.h>
#include <pcl/filters/voxel_grid.h>

int main() {
    using Cloud = pcl::PointCloud<pcl::PointXYZ>;
    Cloud::Ptr sample(new Cloud), voxel(new Cloud);
    sample->push_back({0.01f, 0.01f, 0.01f});
    sample->push_back({0.03f, 0.01f, 0.01f});
    pcl::VoxelGrid<pcl::PointXYZ> vg;
    vg.setInputCloud(sample);
    vg.setLeafSize(0.1f, 0.1f, 0.1f);
    vg.filter(*voxel); // 同体素内点的质心，不是体素中心。
    if (voxel->size()!=1 || std::abs(voxel->at(0).x-0.02f)>1e-6)
        return 1;

    Cloud::Ptr cloud(new Cloud), height(new Cloud), clean(new Cloud);
    for (int i=0; i<30; ++i)
        cloud->push_back({0.01f*i, 0.005f*(i%3), 0.02f*(i%2)});
    cloud->push_back({10.f, 10.f, 0.5f}); // 人为放入一个远离群点。
    cloud->push_back({0.f, 0.f, -1.f}); // 人为放入一个低于范围的点。
    pcl::PassThrough<pcl::PointXYZ> pass;
    pass.setInputCloud(cloud);
    pass.setFilterFieldName("z");
    pass.setFilterLimits(0.f, 0.5f);
    pass.filter(*height);
    pcl::StatisticalOutlierRemoval<pcl::PointXYZ> sor;
    sor.setInputCloud(height);
    sor.setMeanK(6);
    sor.setStddevMulThresh(1.0);
    sor.setNegative(false);
    sor.filter(*clean);
    std::cout << "{\"centroid_x\":" << voxel->at(0).x
              << ",\"input\":" << cloud->size()
              << ",\"height\":" << height->size()
              << ",\"clean\":" << clean->size() << "}\n";
    return height->size()==31 && clean->size()==30 ? 0 : 2;
}
