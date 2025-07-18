document.addEventListener('DOMContentLoaded', function () {
    // 初始化所有图表
    const charts = {
        salary: echarts.init(document.getElementById('salaryChart')),
        sankey: echarts.init(document.getElementById('sankeyChart')),
        heatmap: echarts.init(document.getElementById('heatmapChart')),
        education: echarts.init(document.getElementById('educationChart')),
        positionType: echarts.init(document.getElementById('positionTypeChart')),
        industry: echarts.init(document.getElementById('industryChart')),
        location: echarts.init(document.getElementById('locationChart'))
    };

    // 通用配置
    const commonOptions = {
        backgroundColor: 'transparent',
        textStyle: {
            color: '#e0e0e0',
            fontSize: 14
        },
        title: {
            textStyle: {
                color: '#ffffff',
                fontWeight: 'bold',
                fontSize: 18
            }
        },
        tooltip: {
            backgroundColor: 'rgba(20, 25, 35, 0.9)',
            borderColor: 'rgba(100, 120, 150, 0.4)',
            textStyle: {
                color: '#e0e0e0',
                fontSize: 14
            },
            padding: 10
        },
        grid: {
            containLabel: true,
            left: '8%',
            right: '8%',
            bottom: '12%',
            top: '18%'
        }
    };

    // 错误处理函数
    function handleError(chart, error) {
        console.error('图表渲染失败:', error);
        chart.setOption({
            title: {
                text: '数据加载失败',
                subtext: '请检查网络连接或数据格式',
                left: 'center',
                textStyle: {
                    color: '#ff6b6b',
                    fontSize: 16
                }
            }
        });
    }

    // 封装数据获取和图表设置函数，添加重试机制
    async function fetchAndSetChart(chart, apiUrl, optionGenerator, maxRetries = 3) {
        let retries = 0;
        while (retries < maxRetries) {
            try {
                const response = await fetch(apiUrl);
                if (!response.ok) throw new Error('网络响应失败');
                const data = await response.json();
                console.log(`成功获取 ${apiUrl} 的数据:`, data);
                chart.setOption(optionGenerator(data));
                return;
            } catch (error) {
                retries++;
                if (retries === maxRetries) {
                    handleError(chart, error);
                } else {
                    console.log(`第 ${retries} 次重试请求 ${apiUrl}`);
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }
            }
        }
    }

    // 1. 城市薪资水平对比（箱线图）
    fetchAndSetChart(charts.salary, '/api/salary_comparison', (data) => ({
        ...commonOptions,
        title: {
            text: '城市薪资水平对比',
            subtext: '单位：元/月',
            left: 'center'
        },
        xAxis: {
            type: 'category',
            data: data.map(item => item.city),
            axisLabel: {
                rotate: 45,
                color: '#ccc',
                fontSize: 14
            }
        },
        yAxis: {
            type: 'value',
            name: '月薪(元)',
            axisLabel: {
                color: '#ccc',
                fontSize: 14
            }
        },
        series: [{
            name: '薪资分布',
            type: 'boxplot',
            data: data.map(item => [
                item.min, item.q1, item.median, item.q3, item.max
            ]),
            itemStyle: {
                color: '#3a6ff8'
            }
        }]
    }));

    // 2. 城市→职位类型→行业关联（桑基图）
    fetchAndSetChart(charts.sankey, '/api/job_type_flow', (data) => ({
        ...commonOptions,
        title: {
            text: '城市→职位类型→行业关联',
            left: 'center'
        },
        series: [{
            type: 'sankey',
            layout: 'none',
            data: data.nodes,
            links: data.links,
            categories: data.categories,
            roam: true,
            label: {
                show: true,
                color: '#ccc',
                fontSize: 14
            },
            lineStyle: {
                curveness: 0.3,
                color: 'gradient',
                opacity: 0.6
            }
        }]
    }));

    // 3. 企业规模与经验（热力图）
    fetchAndSetChart(charts.heatmap, '/api/cosize_worktime', (data) => ({
        ...commonOptions,
        title: {
            text: '企业规模与工作经验要求',
            left: 'center'
        },
        xAxis: {
            type: 'category',
            data: data.categories.exp,
            splitArea: {
                show: true,
                areaStyle: {
                    color: 'rgba(255,255,255,0.05)'
                }
            },
            axisLabel: {
                color: '#ccc',
                fontSize: 14
            }
        },
        yAxis: {
            type: 'category',
            data: data.categories.size,
            splitArea: {
                show: true,
                areaStyle: {
                    color: 'rgba(255,255,255,0.05)'
                }
            },
            axisLabel: {
                color: '#ccc',
                fontSize: 14
            }
        },
        visualMap: {
            min: 0,
            max: Math.max(...data.data.flatMap(d => d.data)),
            calculable: true,
            orient: 'horizontal',
            left: 'center',
            bottom: '0%',
            textStyle: {
                color: '#ccc',
                fontSize: 14
            }
        },
        series: [{
            name: '职位数量',
            type: 'heatmap',
            data: data.data.flatMap((sizeData, sizeIdx) =>
                sizeData.data.map((value, expIdx) => [
                    data.categories.exp[expIdx],
                    data.categories.size[sizeIdx],
                    value || 0
                ])
            ),
            label: {
                show: true,
                color: '#fff',
                fontSize: 14
            }
        }]
    }));

    // 4. 学历要求分布（环形图）
    fetchAndSetChart(charts.education, '/api/education_distribution', (data) => ({
        ...commonOptions,
        title: {
            text: '学历要求分布',
            left: 'center'
        },
        legend: {
            type: 'scroll',
            orient: 'horizontal',
            bottom: 10,
            left: 'center',
            pageButtonItemGap: 5,
            pageButtonStyle: {
                color: '#ccc'
            },
            pageTextStyle: {
                color: '#ccc'
            },
            itemWidth: 12,
            itemHeight: 12,
            textStyle: {
                color: '#ccc',
                fontSize: 12
            },
            pageIconColor: '#3a6ff8',
            pageIconInactiveColor: '#666'
        },
        series: [{
            name: '学历要求',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['40%', '50%'],
            data: data,
            itemStyle: {
                borderRadius: 5,
                borderColor: 'rgba(20, 25, 35, 0.8)',
                borderWidth: 2
            },
            label: {
                color: '#ccc',
                fontSize: 14,
                formatter: '{b}: {d}%'
            },
            labelLine: {
                lineStyle: {
                    color: '#999',
                    width: 1
                },
                length: 10,
                length2: 15
            }
        }]
    }));

    // 5. 热门职位类型（折线图）
    fetchAndSetChart(charts.positionType, '/api/position_type_count', (data) => {
        const topData = data.sort((a, b) => b.value - a.value).slice(0, 10);
        return {
            ...commonOptions,
            title: {
                text: '热门职位类型分布',
                left: 'center'
            },
            xAxis: {
                type: 'category',
                data: topData.map(item => item.name),
                axisLabel: {
                    rotate: 45,
                    color: '#ccc',
                    fontSize: 14
                }
            },
            yAxis: {
                type: 'value',
                axisLabel: {
                    color: '#ccc',
                    fontSize: 14
                }
            },
            series: [{
                name: '职位数量',
                data: topData.map(item => item.value),
                type: 'line',
                smooth: true,
                symbol: 'circle',
                symbolSize: 8,
                lineStyle: {
                    color: '#3ad1f8',
                    width: 2
                },
                itemStyle: {
                    color: '#3ad1f8'
                },
                areaStyle: {
                    color: {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 0,
                        y2: 1,
                        colorStops: [{
                            offset: 0, color: 'rgba(58, 209, 248, 0.3)'
                        }, {
                            offset: 1, color: 'rgba(58, 209, 248, 0)'
                        }]
                    }
                }
            }]
        };
    });

    // 6. 热门行业分布（柱状图）
    fetchAndSetChart(charts.industry, '/api/industry_count', (data) => {
        const topData = data.sort((a, b) => b.value - a.value).slice(0, 10);
        return {
            ...commonOptions,
            title: {
                text: '热门行业分布',
                left: 'center'
            },
            xAxis: {
                type: 'category',
                data: topData.map(item => item.name),
                axisLabel: {
                    rotate: 45,
                    color: '#ccc',
                    fontSize: 14
                }
            },
            yAxis: {
                type: 'value',
                axisLabel: {
                    color: '#ccc',
                    fontSize: 14
                }
            },
            series: [{
                name: '职位数量',
                data: topData.map(item => item.value),
                type: 'bar',
                barWidth: '60%',
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(
                        0, 0, 0, 1,
                        [
                            {offset: 0, color: '#3a6ff8'},
                            {offset: 1, color: '#3ad1f8'}
                        ]
                    ),
                    borderRadius: 6
                },
                label: {
                    show: true,
                    position: 'top',
                    color: '#fff',
                    fontSize: 14
                }
            }]
        };
    });

    // 城市-省份映射表（简化版）
    const cityToProvinceMap = {
        // 华东地区
        "上海": "上海",
        "南京": "江苏",
        "无锡": "江苏",
        "苏州": "江苏",
        "镇江": "江苏",
        "杭州": "浙江",
        "宁波": "浙江",
        "合肥": "安徽",
        "江阴市": "江苏",
        "北京": "北京",
        "广州": "广东",
        "深圳": "广东",
    };

    // 7. 工作地点分布（地图）
    fetchAndSetChart(charts.location, '/api/location_count', (data) => {
        // 预加载地图数据
        if (!echarts.getMap('china')) {
            console.error('中国地图数据未加载，尝试动态加载...');
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/echarts@5.4.2/map/js/china.js';
            script.onload = () => renderMapChart(processCityData(data));
            document.body.appendChild(script);

            return {
                title: {
                    text: '地图数据加载中...',
                    left: 'center'
                }
            };
        } else {
            return renderMapChart(processCityData(data));
        }
    });

    // 数据预处理函数：将市级数据转换为省级数据
    function processCityData(cityData) {
        // 创建省份数据容器
        const provinceData = {};

        // 遍历市级数据，聚合到省份
        cityData.forEach(cityItem => {
            const cityName = cityItem.name;
            const cityValue = cityItem.value;

            // 从映射表中查找对应的省份
            const provinceName = cityToProvinceMap[cityName];

            if (provinceName) {
                // 如果该省份已存在，累加值；否则初始化
                if (provinceData[provinceName]) {
                    provinceData[provinceName] += cityValue;
                } else {
                    provinceData[provinceName] = cityValue;
                }
            } else {
                console.warn(`未找到城市 "${cityName}" 的省份映射`);
            }
        });

        // 将对象转换为ECharts需要的数组格式
        return Object.keys(provinceData).map(provinceName => ({
            name: provinceName,
            value: provinceData[provinceName]
        }));
    }

    // 地图渲染函数
    function renderMapChart(data) {
        return {
            ...commonOptions,
            title: {
                text: '工作地点分布',
                subtext: '按省份职位数量',
                left: 'center'
            },
            visualMap: {
                min: 0,
                max: Math.max(...data.map(item => item.value)),
                calculable: true,
                orient: 'horizontal',
                left: 'center',
                bottom: '10%',
                textStyle: {
                    color: '#ccc',
                    fontSize: 14
                },
                inRange: {
                    color: ['#e0ecff', '#91bfdb', '#43a2ca', '#0868ac']
                }
            },
            series: [{
                name: '职位数量',
                type: 'map',
                mapType: 'china',
                roam: true,
                zoom: 1.2,
                label: {
                    show: true,
                    color: '#ccc',
                    fontSize: 12
                },
                itemStyle: {
                    normal: {
                        borderColor: 'rgba(255,255,255,0.2)',
                        borderWidth: 1
                    },
                    emphasis: {
                        areaColor: '#3a6ff8',
                        shadowBlur: 20,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                },
                data: data
            }]
        };
    }

    // 响应窗口大小变化
    window.addEventListener('resize', function () {
        Object.values(charts).forEach(chart => chart.resize());
    });
});