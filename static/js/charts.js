// 全局变量存储最近的预测记录ID
let lastPredictionRecordId = null;

document.addEventListener("DOMContentLoaded", function () {
  // 导航栏交互增强
  function initNavbarInteractions() {
    const navLinks = document.querySelectorAll(".nav-link");

    navLinks.forEach((link) => {
      link.addEventListener("click", function (e) {
        // 添加点击动画效果
        this.style.transform = "scale(0.95)";
        setTimeout(() => {
          this.style.transform = "";
        }, 150);
      });
    });

    // 导航栏滚动效果
    let lastScrollTop = 0;
    const navbar = document.querySelector(".navbar");

    if (navbar) {
      window.addEventListener("scroll", function () {
        const scrollTop =
          window.pageYOffset || document.documentElement.scrollTop;

        if (scrollTop > lastScrollTop && scrollTop > 100) {
          // 向下滚动时隐藏导航栏
          navbar.style.transform = "translateY(-100%)";
        } else {
          // 向上滚动时显示导航栏
          navbar.style.transform = "translateY(0)";
        }

        lastScrollTop = scrollTop;
      });
    }
  }

  // 初始化导航栏交互
  initNavbarInteractions();
  // 初始化所有图表
  const charts = {
    killWinRate: echarts.init(document.getElementById("killWinRateChart")),
    assistWinRate: echarts.init(document.getElementById("assistWinRateChart")),
    vehicleDistance: echarts.init(
      document.getElementById("vehicleDistanceChart")
    ),
    partySizeKills: echarts.init(
      document.getElementById("partySizeKillsChart")
    ),
    killDistance: echarts.init(document.getElementById("killDistanceChart")),
    weaponKills: echarts.init(document.getElementById("weaponKillsChart")),
    weaponDistance: echarts.init(
      document.getElementById("weaponDistanceChart")
    ),
    interactiveWeapon: echarts.init(
      document.getElementById("interactiveWeaponChart")
    ),
  };

  // 通用配置
  const commonOptions = {
    backgroundColor: "transparent",
    textStyle: {
      color: "#e0e0e0",
      fontSize: 14,
    },
    title: {
      textStyle: {
        color: "#ffffff",
        fontWeight: "bold",
        fontSize: 18,
      },
    },
    tooltip: {
      backgroundColor: "rgba(20, 25, 35, 0.9)",
      borderColor: "rgba(100, 120, 150, 0.4)",
      textStyle: {
        color: "#e0e0e0",
        fontSize: 14,
      },
      padding: 10,
    },
    grid: {
      containLabel: true,
      left: "8%",
      right: "8%",
      bottom: "12%",
      top: "18%",
    },
  };

  // 错误处理函数
  function handleError(chart, error) {
    console.error("图表渲染失败:", error);
    chart.setOption({
      title: {
        text: "数据加载失败",
        left: "center",
        top: "middle",
        textStyle: {
          color: "#ff6b6b",
          fontSize: 16,
        },
      },
    });
  }

  // 通用数据获取和图表设置函数
  function fetchAndSetChart(chart, url, optionGenerator) {
    fetch(url)
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          throw new Error(data.error);
        }
        const option = optionGenerator(data);
        chart.setOption(option);
      })
      .catch((error) => handleError(chart, error));
  }

  // 1. 击杀人数与吃鸡概率关系 - 改为折线图显示趋势
  fetchAndSetChart(charts.killWinRate, "/api/kill-win-rate", (data) => ({
    ...commonOptions,
    title: {
      text: "队伍击杀数与吃鸡概率趋势分析",
      left: "center",
      textStyle: {
        color: "#f97316",
        fontSize: 22,
        fontWeight: "bold",
      },
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "cross",
        label: {
          backgroundColor: "#6a7985",
        },
      },
      formatter: "击杀数: {b}<br/>吃鸡概率: {c}%",
    },
    xAxis: {
      type: "category",
      data: data.map((item) => item.kills),
      axisLabel: {
        color: "#ccc",
        fontSize: 14,
        fontWeight: "bold",
      },
      axisLine: {
        show: true,
        lineStyle: {
          color: "#ccc",
        },
      },
    },
    yAxis: {
      type: "value",
      name: "吃鸡概率 (%)",
      nameTextStyle: {
        color: "#ccc",
        fontSize: 14,
        fontWeight: "bold",
      },
      axisLabel: {
        color: "#ccc",
        fontSize: 14,
        formatter: "{value}%",
      },
      splitLine: {
        lineStyle: {
          type: "dashed",
          color: "rgba(255, 255, 255, 0.1)",
        },
      },
    },
    series: [
      {
        name: "吃鸡概率",
        type: "line",
        smooth: true,
        symbol: "circle",
        symbolSize: 10,
        data: data.map((item) => (item.win_rate * 100).toFixed(2)),
        lineStyle: {
          color: "#f97316",
          width: 5,
          shadowColor: "rgba(249, 115, 22, 0.5)",
          shadowBlur: 15,
          shadowOffsetY: 4,
        },
        itemStyle: {
          color: "#f97316",
          borderColor: "#fff",
          borderWidth: 3,
          shadowColor: "rgba(249, 115, 22, 0.6)",
          shadowBlur: 8,
        },
        areaStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: "rgba(249, 115, 22, 0.4)" },
              { offset: 0.3, color: "rgba(249, 115, 22, 0.25)" },
              { offset: 0.7, color: "rgba(249, 115, 22, 0.1)" },
              { offset: 1, color: "rgba(249, 115, 22, 0.02)" },
            ],
          },
        },
        markPoint: {
          data: [
            { type: "max", name: "最高概率" },
            { type: "min", name: "最低概率" },
          ],
          itemStyle: {
            color: "#ff6b6b",
            borderColor: "#fff",
            borderWidth: 2,
            shadowColor: "rgba(255, 107, 107, 0.5)",
            shadowBlur: 10,
          },
          label: {
            color: "#fff",
            fontWeight: "bold",
            fontSize: 12,
          },
        },
        emphasis: {
          focus: "series",
          lineStyle: {
            width: 6,
          },
          itemStyle: {
            shadowBlur: 12,
            shadowColor: "rgba(249, 115, 22, 0.8)",
          },
        },
      },
    ],
  }));

  // 2. 助攻次数与吃鸡概率关系 - 改为面积图显示累积效果
  fetchAndSetChart(charts.assistWinRate, "/api/assist-win-rate", (data) => ({
    ...commonOptions,
    title: {
      text: "助攻次数与吃鸡概率累积分析",
      left: "center",
      textStyle: {
        color: "#22d3ee",
        fontSize: 22,
        fontWeight: "bold",
      },
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "cross",
      },
      formatter: "助攻次数: {b}<br/>吃鸡概率: {c}%",
    },
    xAxis: {
      type: "category",
      data: data.map((item) => item.assists),
      axisLabel: {
        color: "#ccc",
        fontSize: 14,
        fontWeight: "bold",
      },
      axisLine: {
        show: true,
        lineStyle: {
          color: "#ccc",
        },
      },
    },
    yAxis: {
      type: "value",
      name: "吃鸡概率 (%)",
      nameTextStyle: {
        color: "#ccc",
        fontSize: 14,
        fontWeight: "bold",
      },
      axisLabel: {
        color: "#ccc",
        fontSize: 14,
        formatter: "{value}%",
      },
      splitLine: {
        lineStyle: {
          type: "dashed",
          color: "rgba(255, 255, 255, 0.1)",
        },
      },
    },
    series: [
      {
        name: "吃鸡概率",
        type: "line",
        smooth: true,
        symbol: "diamond",
        symbolSize: 12,
        data: data.map((item) => (item.win_rate * 100).toFixed(2)),
        lineStyle: {
          color: "#22d3ee",
          width: 4,
          shadowColor: "rgba(34, 211, 238, 0.5)",
          shadowBlur: 12,
          shadowOffsetY: 3,
        },
        itemStyle: {
          color: "#22d3ee",
          borderColor: "#fff",
          borderWidth: 3,
          shadowColor: "rgba(34, 211, 238, 0.7)",
          shadowBlur: 10,
        },
        areaStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: "rgba(34, 211, 238, 0.5)" },
              { offset: 0.2, color: "rgba(34, 211, 238, 0.35)" },
              { offset: 0.5, color: "rgba(34, 211, 238, 0.2)" },
              { offset: 0.8, color: "rgba(34, 211, 238, 0.08)" },
              { offset: 1, color: "rgba(34, 211, 238, 0.02)" },
            ],
          },
        },
        markLine: {
          data: [{ type: "average", name: "平均概率" }],
          lineStyle: {
            color: "#667eea",
            type: "dashed",
            width: 2,
            shadowColor: "rgba(102, 126, 234, 0.4)",
            shadowBlur: 6,
          },
          label: {
            color: "#667eea",
            fontWeight: "bold",
            fontSize: 11,
          },
        },
        emphasis: {
          focus: "series",
          lineStyle: {
            width: 5,
            shadowBlur: 15,
            shadowColor: "rgba(34, 211, 238, 0.8)",
          },
          itemStyle: {
            shadowBlur: 15,
            shadowColor: "rgba(34, 211, 238, 0.9)",
            borderWidth: 4,
          },
        },
      },
    ],
  }));

  // 3. 搭乘车辆里程与吃鸡概率 - 改为饼图显示分布
  fetchAndSetChart(
    charts.vehicleDistance,
    "/api/vehicle-distance-win",
    (data) => ({
      ...commonOptions,
      title: {
        text: "搭乘车辆里程分布与吃鸡概率",
        left: "center",
        textStyle: {
          color: "#fbbf24",
          fontSize: 22,
          fontWeight: "bold",
        },
      },
      tooltip: {
        trigger: "item",
        formatter: "{a} <br/>{b}: {c}% ({d}%)",
      },
      // 移除图例，使用标签显示
      legend: {
        show: false,
      },
      series: [
        {
          name: "吃鸡概率",
          type: "pie",
          radius: ["40%", "70%"],
          center: ["50%", "50%"],
          avoidLabelOverlap: false,
          itemStyle: {
            borderWidth: 0,
            shadowBlur: 10,
            shadowColor: "rgba(0, 0, 0, 0.4)",
            shadowOffsetX: 0,
            shadowOffsetY: 3,
          },
          label: {
            show: true,
            position: "outside",
            formatter: "{b}: {d}%",
            fontSize: 12,
            fontWeight: "bold",
            color: "#fff",
            textShadowColor: "rgba(0, 0, 0, 0.8)",
            textShadowBlur: 2,
            distanceToLabelLine: 5,
          },
          labelLine: {
            show: true,
            length: 15,
            length2: 10,
            smooth: false,
            lineStyle: {
              color: "#ccc",
              width: 1,
              opacity: 0.8,
            },
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 15,
              shadowOffsetX: 0,
              shadowOffsetY: 5,
              shadowColor: "rgba(0, 0, 0, 0.6)",
            },
            scale: true,
            scaleSize: 8,
          },
          data: data.map((item, index) => ({
            value: (item.win_rate * 100).toFixed(2),
            name: item.distance_range,
            itemStyle: {
              // 使用参考图片中的颜色方案
              color: [
                "#FF7F50", // 橙色 - 对应参考图片中的主要橙色扇形
                "#4CAF50", // 绿色 - 对应参考图片中的绿色扇形
                "#2196F3", // 蓝色 - 对应参考图片中的蓝色扇形
                "#FFC107", // 黄色 - 对应参考图片中的黄色小扇形
                "#F44336", // 红色 - 对应参考图片中的红色小扇形
                "#9C27B0", // 紫色 - 其他小扇形
                "#00BCD4", // 青色 - 其他小扇形
                "#795548", // 棕色 - 其他小扇形
              ][index % 8],
              opacity: 0.95,
              shadowBlur: 5,
              shadowColor: "rgba(0, 0, 0, 0.2)",
            },
          })),
        },
      ],
    })
  );

  // 4. 击杀距离分布
  fetchAndSetChart(charts.killDistance, "/api/kill-distance", (data) => ({
    ...commonOptions,
    title: {
      text: "击杀距离分布 (<400米)",
      left: "center",
      textStyle: {
        // 使用 textStyle 进行更详细的样式控制
        color: "#22d3ee",
        fontSize: 22, // 显著增大字号
        fontWeight: "bold", // 字体加粗
      },
    },
    xAxis: {
      type: "value",
      name: "击杀距离 (米)",
      axisLabel: {
        color: "#ccc",
        fontSize: 12,
      },
    },
    yAxis: {
      type: "value",
      name: "频次",
      axisLabel: {
        color: "#ccc",
        fontSize: 12,
      },
    },
    series: [
      {
        name: "击杀频次",
        type: "line",
        data: data.map((item) => [item.distance, item.count]),
        smooth: true,
        lineStyle: {
          color: "#45b7d1",
          width: 3,
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(69, 183, 209, 0.6)" },
            { offset: 1, color: "rgba(69, 183, 209, 0.1)" },
          ]),
        },
      },
    ],
  }));

  // 5. 武器击杀统计对比 - 改为雷达图显示多维对比
  fetchAndSetChart(charts.weaponKills, "/api/weapon-kills", (data) => ({
    ...commonOptions,
    title: {
      text: "武器击杀统计雷达对比",
      left: "center",
      textStyle: {
        color: "#22d3ee",
        fontSize: 22,
        fontWeight: "bold",
      },
    },
    tooltip: {
      trigger: "item",
    },
    legend: {
      data: ["Erangel", "Miramar"],
      textStyle: {
        color: "#ccc",
        fontSize: 14,
      },
      top: "8%",
    },
    radar: {
      indicator: data.erangel.map((item) => ({
        name: item.weapon,
        max:
          Math.max(
            ...data.erangel.map((w) => w.kills),
            ...data.miramar.map((w) => w.kills)
          ) * 1.2,
      })),
      center: ["50%", "55%"],
      radius: "65%",
      axisName: {
        color: "#ccc",
        fontSize: 12,
      },
      splitArea: {
        areaStyle: {
          color: ["rgba(255, 255, 255, 0.02)", "rgba(255, 255, 255, 0.05)"],
        },
      },
      splitLine: {
        lineStyle: {
          color: "rgba(255, 255, 255, 0.1)",
        },
      },
      axisLine: {
        lineStyle: {
          color: "rgba(255, 255, 255, 0.2)",
        },
      },
    },
    series: [
      {
        name: "武器击杀对比",
        type: "radar",
        data: [
          {
            value: data.erangel.map((item) => item.kills),
            name: "Erangel",
            itemStyle: {
              color: "#4ecdc4",
            },
            areaStyle: {
              color: "rgba(78, 205, 196, 0.2)",
            },
            lineStyle: {
              color: "#4ecdc4",
              width: 3,
            },
          },
          {
            value: data.miramar.map((item) => item.kills),
            name: "Miramar",
            itemStyle: {
              color: "#ff6b6b",
            },
            areaStyle: {
              color: "rgba(255, 107, 107, 0.2)",
            },
            lineStyle: {
              color: "#ff6b6b",
              width: 3,
            },
          },
        ],
      },
    ],
  }));

  // 6. 队伍规模与击杀数分布
  fetchAndSetChart(charts.partySizeKills, "/api/party-size-kills", (data) => {
    const series = [];
    const partyKeys = Object.keys(data);

    partyKeys.forEach((key, index) => {
      const partySize = key.replace("party_", "");
      series.push({
        name: `${partySize}人队伍`,
        type: "bar",
        data: data[key].map((item) => item.count),
        itemStyle: {
          color: ["#4ecdc4", "#667eea", "#ff6b6b", "#96ceb4"][index % 4],
        },
      });
    });

    return {
      ...commonOptions,
      title: {
        text: "队伍规模与击杀数分布",
        left: "center",
        textStyle: {
          // 使用 textStyle 进行更详细的样式控制
          color: "#22d3ee",
          fontSize: 22, // 显著增大字号
          fontWeight: "bold", // 字体加粗
        },
      },
      legend: {
        data: series.map((s) => s.name),
        textStyle: {
          color: "#ccc",
        },
        top: "10%",
      },
      xAxis: {
        type: "category",
        data: data[partyKeys[0]].map((item) => item.kills),
        axisLabel: {
          color: "#ccc",
          fontSize: 12,
        },
      },
      yAxis: {
        type: "value",
        name: "数量",
        axisLabel: {
          color: "#ccc",
          fontSize: 12,
        },
      },
      series: series,
    };
  });

  // 7. 不同距离武器击杀统计
  fetchAndSetChart(
    charts.weaponDistance,
    "/api/weapon-distance-analysis",
    (data) => ({
      ...commonOptions,
      title: {
        text: "不同距离武器击杀统计",
        left: "center",
        textStyle: {
          // 使用 textStyle 进行更详细的样式控制
          color: "#22d3ee",
          fontSize: 22, // 显著增大字号
          fontWeight: "bold", // 字体加粗
        },
      },
      legend: {
        data: ["Erangel狙击", "Erangel近战", "Miramar狙击", "Miramar近战"],
        textStyle: {
          color: "#ccc",
        },
        top: "10%",
      },
      xAxis: {
        type: "category",
        data: ["狙击武器(50-1500m)", "近战武器(<50m)"],
        axisLabel: {
          color: "#ccc",
          fontSize: 12,
        },
      },
      yAxis: {
        type: "value",
        name: "击杀数",
        axisLabel: {
          color: "#ccc",
          fontSize: 12,
        },
      },
      series: [
        {
          name: "Erangel狙击",
          type: "bar",
          data: [
            Object.values(data.erangel.sniper).reduce((a, b) => a + b, 0),
            0,
          ],
          itemStyle: { color: "#4ecdc4" },
        },
        {
          name: "Erangel近战",
          type: "bar",
          data: [
            0,
            Object.values(data.erangel.melee).reduce((a, b) => a + b, 0),
          ],
          itemStyle: { color: "#667eea" },
        },
        {
          name: "Miramar狙击",
          type: "bar",
          data: [
            Object.values(data.miramar.sniper).reduce((a, b) => a + b, 0),
            0,
          ],
          itemStyle: { color: "#ff6b6b" },
        },
        {
          name: "Miramar近战",
          type: "bar",
          data: [
            0,
            Object.values(data.miramar.melee).reduce((a, b) => a + b, 0),
          ],
          itemStyle: { color: "#96ceb4" },
        },
      ],
    })
  );

  // 8. 交互式武器分析
  fetchAndSetChart(
    charts.interactiveWeapon,
    "/api/interactive-weapon-analysis",
    (data) => ({
      ...commonOptions,
      title: {
        text: "交互式武器分析 - 武器与击杀距离关系",
        left: "center",
        textStyle: {
          // 使用 textStyle 进行更详细的样式控制
          color: "#22d3ee",
          fontSize: 22, // 显著增大字号
          fontWeight: "bold", // 字体加粗
        },
      },
      legend: {
        data: ["Erangel", "Miramar"],
        textStyle: {
          color: "#ccc",
        },
        top: "10%",
      },
      xAxis: {
        type: "value",
        name: "击杀距离 (米)",
        axisLabel: {
          color: "#ccc",
          fontSize: 12,
        },
      },
      yAxis: {
        type: "category",
        data: [...new Set([...data.erangel.weapons, ...data.miramar.weapons])],
        axisLabel: {
          color: "#ccc",
          fontSize: 10,
        },
      },
      series: [
        {
          name: "Erangel",
          type: "scatter",
          data: data.erangel.data.map((item) => [
            item.distance,
            item.killed_by,
          ]),
          itemStyle: {
            color: "#4ecdc4",
            opacity: 0.7,
          },
          symbolSize: 8,
        },
        {
          name: "Miramar",
          type: "scatter",
          data: data.miramar.data.map((item) => [
            item.distance,
            item.killed_by,
          ]),
          itemStyle: {
            color: "#ff6b6b",
            opacity: 0.7,
          },
          symbolSize: 8,
        },
      ],
    })
  );

  // 热力图现在使用PNG图片显示，添加交互增强
  function initHeatmapInteractions() {
    const heatmapImages = document.querySelectorAll(".heatmap-image");

    heatmapImages.forEach((img, index) => {
      // 添加加载事件监听
      img.addEventListener("load", function () {
        console.log(`热力图 ${index + 1} 加载成功`);
        this.style.opacity = "0";
        this.style.transform = "scale(0.95)";

        // 淡入动画
        setTimeout(() => {
          this.style.transition = "all 0.5s ease";
          this.style.opacity = "1";
          this.style.transform = "scale(1)";
        }, 100);
      });

      // 添加错误处理
      img.addEventListener("error", function () {
        console.error(`热力图 ${index + 1} 加载失败`);
        const placeholder = this.nextElementSibling;
        if (
          placeholder &&
          placeholder.classList.contains("heatmap-placeholder")
        ) {
          placeholder.style.display = "flex";
          placeholder.style.animation = "fadeIn 0.3s ease";
        }
      });

      // 添加点击放大功能
      img.addEventListener("click", function () {
        if (this.style.transform.includes("scale(1.5)")) {
          this.style.transform = "scale(1)";
          this.style.cursor = "zoom-in";
        } else {
          this.style.transform = "scale(1.5)";
          this.style.cursor = "zoom-out";
          this.style.zIndex = "1000";
        }
      });

      // 初始设置
      img.style.cursor = "zoom-in";
    });
  }

  // 初始化热力图交互
  initHeatmapInteractions();

  // PUBG吃鸡概率预测功能
  const predictionForm = document.getElementById("predictionForm");
  const predictionResult = document.getElementById("predictionResult");

  if (predictionForm) {
    predictionForm.addEventListener("submit", async function (e) {
      e.preventDefault();

      // 获取表单数据
      const formData = new FormData(predictionForm);
      const data = {};
      for (let [key, value] of formData.entries()) {
        data[key] = parseFloat(value);
      }

      console.log("发送预测请求:", data);

      // 显示加载状态
      updatePredictionResult("loading");

      try {
        const response = await fetch("/api/predict", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        });

        const result = await response.json();
        console.log("预测结果:", result);

        if (response.ok) {
          updatePredictionResult("success", result);
        } else {
          updatePredictionResult("error", result);
        }
      } catch (error) {
        console.error("预测请求失败:", error);
        updatePredictionResult("error", {
          error: "网络请求失败，请检查连接",
        });
      }
    });
  }

  function updatePredictionResult(status, data = null) {
    const percentageElement = predictionResult.querySelector(".percentage");
    const confidenceElement =
      predictionResult.querySelector(".confidence-value");
    const tipsElement = predictionResult.querySelector(".prediction-tips p");
    const circleProgress = predictionResult.querySelector(".circle-progress");

    switch (status) {
      case "loading":
        percentageElement.textContent = "...";
        confidenceElement.textContent = "计算中";
        confidenceElement.className = "confidence-value";
        tipsElement.textContent = "正在使用AI模型分析您的游戏数据...";
        circleProgress.style.background =
          "conic-gradient(#667eea 0deg, #667eea 90deg, rgba(255, 255, 255, 0.1) 90deg)";
        break;

      case "success":
        const percentage = data.percentage;
        const probability = data.probability;
        const confidence = data.confidence;

        // 保存预测记录ID，用于后续AI建议关联
        if (data.record_id) {
          lastPredictionRecordId = data.record_id;
          console.log("预测记录ID已保存:", lastPredictionRecordId);
        }

        percentageElement.textContent = `${percentage}%`;
        confidenceElement.textContent = confidence;
        confidenceElement.className = `confidence-value ${confidence}`;

        // 更新圆形进度条
        const degrees = percentage * 3.6; // 转换为角度
        let color = "#4ecdc4"; // 默认绿色
        if (percentage < 30) {
          color = "#ff6b6b"; // 红色
        } else if (percentage < 60) {
          color = "#667eea"; // 蓝色
        }

        circleProgress.style.background = `conic-gradient(${color} 0deg, ${color} ${degrees}deg, rgba(255, 255, 255, 0.1) ${degrees}deg)`;

        // 更新提示信息
        let tips = "";
        if (percentage >= 70) {
          tips = "🎉 恭喜！您有很高的吃鸡概率！保持当前策略，稳扎稳打！";
        } else if (percentage >= 50) {
          tips = "💪 不错的表现！继续提升击杀数和生存时间，胜利在望！";
        } else if (percentage >= 30) {
          tips = "⚡ 还有提升空间！尝试更积极的游戏策略，增加击杀和伤害输出。";
        } else {
          tips = "🎯 需要调整策略！建议提高生存时间，寻找更好的装备和位置。";
        }
        tipsElement.textContent = tips;
        break;

      case "error":
        percentageElement.textContent = "错误";
        confidenceElement.textContent = "失败";
        confidenceElement.className = "confidence-value medium";
        tipsElement.textContent = `预测失败: ${data.error || "未知错误"}`;
        circleProgress.style.background =
          "conic-gradient(#ff6b6b 0deg, #ff6b6b 90deg, rgba(255, 255, 255, 0.1) 90deg)";
        break;
    }
  }

  // 窗口大小改变时重新调整图表
  window.addEventListener("resize", function () {
    Object.values(charts).forEach((chart) => {
      chart.resize();
    });
  });

  // AI建议生成功能
  const generateAdviceBtn = document.getElementById("generateAdviceBtn");
  const adviceResult = document.getElementById("adviceResult");
  const adviceText = document.querySelector(".advice-text");

  if (generateAdviceBtn) {
    generateAdviceBtn.addEventListener("click", async function () {
      console.log("开始生成AI建议");

      // 显示加载状态
      const btnText = generateAdviceBtn.querySelector(".btn-text");
      const btnLoading = generateAdviceBtn.querySelector(".btn-loading");

      btnText.style.display = "none";
      btnLoading.style.display = "inline";
      generateAdviceBtn.disabled = true;

      // 隐藏之前的结果
      adviceResult.style.display = "none";

      try {
        // 构建请求体，包含关联的预测记录ID
        const requestBody = {};
        if (lastPredictionRecordId) {
          requestBody.record_id = lastPredictionRecordId;
          console.log("关联预测记录ID:", lastPredictionRecordId);
        }

        const response = await fetch("/api/generate-advice", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(requestBody),
        });

        const result = await response.json();
        console.log("AI建议生成结果:", result);

        if (response.ok && result.success) {
          // 显示建议内容
          adviceText.innerHTML = formatAdviceContent(result.advice);
          adviceResult.style.display = "block";

          // 滚动到建议区域
          adviceResult.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
        } else {
          // 显示错误信息
          adviceText.innerHTML = `<div style="color: #ff6b6b; text-align: center;">
            <strong>生成失败</strong><br>
            ${result.error || "未知错误，请稍后重试"}
          </div>`;
          adviceResult.style.display = "block";
        }
      } catch (error) {
        console.error("AI建议生成请求失败:", error);
        adviceText.innerHTML = `<div style="color: #ff6b6b; text-align: center;">
          <strong>网络请求失败</strong><br>
          请检查网络连接后重试
        </div>`;
        adviceResult.style.display = "block";
      } finally {
        // 恢复按钮状态
        btnText.style.display = "inline";
        btnLoading.style.display = "none";
        generateAdviceBtn.disabled = false;
      }
    });
  }

  // 格式化建议内容
  function formatAdviceContent(content) {
    if (!content) return "";

    // 将markdown格式转换为HTML
    let formatted = content
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>") // 粗体
      .replace(/\*(.*?)\*/g, "<em>$1</em>") // 斜体
      .replace(/\n\n/g, "</p><p>") // 段落
      .replace(/\n/g, "<br>"); // 换行

    // 包装在段落标签中
    formatted = "<p>" + formatted + "</p>";

    return formatted;
  }
});
