document.addEventListener("DOMContentLoaded", function () {
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

  // 1. 击杀人数与吃鸡概率关系
  fetchAndSetChart(charts.killWinRate, "/api/kill-win-rate", (data) => ({
    ...commonOptions,
    title: {
      text: "击杀人数与吃鸡概率关系",
      left: "center",
    },
    xAxis: {
      type: "category",
      data: data.map((item) => item.kills),
      axisLabel: {
        color: "#ccc",
        fontSize: 12,
      },
    },
    yAxis: {
      type: "value",
      name: "吃鸡概率",
      axisLabel: {
        color: "#ccc",
        fontSize: 12,
        formatter: "{value}%",
      },
    },
    series: [
      {
        name: "吃鸡概率",
        type: "bar",
        data: data.map((item) => (item.win_rate * 100).toFixed(2)),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "#4ecdc4" },
            { offset: 1, color: "#44a08d" },
          ]),
        },
      },
    ],
  }));

  // 2. 助攻次数与吃鸡概率关系
  fetchAndSetChart(charts.assistWinRate, "/api/assist-win-rate", (data) => ({
    ...commonOptions,
    title: {
      text: "助攻次数与吃鸡概率关系",
      left: "center",
    },
    xAxis: {
      type: "category",
      data: data.map((item) => item.assists),
      axisLabel: {
        color: "#ccc",
        fontSize: 12,
      },
    },
    yAxis: {
      type: "value",
      name: "吃鸡概率",
      axisLabel: {
        color: "#ccc",
        fontSize: 12,
        formatter: "{value}%",
      },
    },
    series: [
      {
        name: "吃鸡概率",
        type: "bar",
        data: data.map((item) => (item.win_rate * 100).toFixed(2)),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "#667eea" },
            { offset: 1, color: "#764ba2" },
          ]),
        },
      },
    ],
  }));

  // 3. 搭乘车辆里程与吃鸡概率
  fetchAndSetChart(
    charts.vehicleDistance,
    "/api/vehicle-distance-win",
    (data) => ({
      ...commonOptions,
      title: {
        text: "搭乘车辆里程与吃鸡概率",
        left: "center",
      },
      xAxis: {
        type: "category",
        data: data.map((item) => item.distance_range),
        axisLabel: {
          color: "#ccc",
          fontSize: 12,
          rotate: 45,
        },
      },
      yAxis: {
        type: "value",
        name: "吃鸡概率",
        axisLabel: {
          color: "#ccc",
          fontSize: 12,
          formatter: "{value}%",
        },
      },
      series: [
        {
          name: "吃鸡概率",
          type: "bar",
          data: data.map((item) => (item.win_rate * 100).toFixed(2)),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: "#ff6b6b" },
              { offset: 1, color: "#ee5a24" },
            ]),
          },
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

  // 5. 武器击杀统计对比
  fetchAndSetChart(charts.weaponKills, "/api/weapon-kills", (data) => ({
    ...commonOptions,
    title: {
      text: "武器击杀统计对比",
      left: "center",
    },
    legend: {
      data: ["Erangel", "Miramar"],
      textStyle: {
        color: "#ccc",
      },
      top: "10%",
    },
    xAxis: {
      type: "category",
      data: data.erangel.map((item) => item.weapon),
      axisLabel: {
        color: "#ccc",
        fontSize: 10,
        rotate: 45,
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
        name: "Erangel",
        type: "bar",
        data: data.erangel.map((item) => item.kills),
        itemStyle: {
          color: "#4ecdc4",
        },
      },
      {
        name: "Miramar",
        type: "bar",
        data: data.miramar.map((item) => item.kills),
        itemStyle: {
          color: "#ff6b6b",
        },
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
        data: ["狙击武器(800-1500m)", "近战武器(<10m)"],
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
});
