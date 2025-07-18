import React, { useState, useEffect } from "react";
import "./HomePage.css"; // 引入自定义样式

// 增强图片组件，支持加载失败时使用原始URL重试
const EnhancedImage = ({ primarySrc, fallbackSrc, alt, className, style }) => {
  const [src, setSrc] = useState(primarySrc);
  const [errorOccurred, setErrorOccurred] = useState(false);

  useEffect(() => {
    setSrc(primarySrc);
    setErrorOccurred(false);
  }, [primarySrc]);

  const handleError = () => {
    // 如果有备用URL且未使用过，则切换为备用URL
    if (!errorOccurred && fallbackSrc && fallbackSrc !== primarySrc) {
      setSrc(fallbackSrc);
      setErrorOccurred(true);
    }
  };

  return (
    <img
      src={src}
      alt={alt}
      className={className}
      style={style}
      onError={handleError}
    />
  );
};

const HomePage = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [loading, setLoading] = useState(false);
  const [photos, setPhotos] = useState<
    {
      id: number;
      url: string;
      description: string;
      type: number;
      originalUrl: string;
    }[]
  >([]); // 定义 photos 状态
  const purchase = 0;

  const fetchStats = async () => {
    try {
      setLoading(true);
      let apiUrl = "/api/stats/random/4";

      const response = await fetch(apiUrl);
      if (!response.ok) {
        throw new Error(`请求失败: ${response.status}`);
      }
      const result = await response.json();

      setPhotos(
        result.data.map((photo) => {
          // 保留原始URL用于回退
          const originalUrl = photo.url;
          // 创建带质量参数的URL
          const imageUrl = new URL(photo.url);
          imageUrl.searchParams.set("x-oss-process", "image/quality,q_85");

          return {
            id: photo.id,
            url: imageUrl.toString(), // 显示用的URL（带质量参数）
            originalUrl: originalUrl, // 原始URL用于加载失败时回退
            description: photo.description,
            type: photo.type,
          };
        })
      );
    } catch (error) {
      console.error("获取照片失败:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();

    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener("scroll", handleScroll);
    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);

  return (
    <div
      className="s-content s-font-body-gotham-rounded"
      style={{ backgroundColor: "#fff" }}
    >
      {/* 顶部标题 - 滚动时会折叠 */}
      <div className={`brand-header ${isScrolled ? "collapsed" : ""}`}>
        <h1 className="brand-title">223nobody自由摄影师</h1>
      </div>

      {/* 导航栏 */}
      <nav className={`navbar ${isScrolled ? "scrolled" : ""}`}>
        <ul
          style={{
            display: "flex",
            justifyContent: "center",
            listStyle: "none",
            marginTop: "20px",
            gap: "30px",
          }}
        >
          <li>
            <a href="/" className="nav-link1">
              首页
            </a>
          </li>
          <li>
            <a href="/works" className="nav-link">
              作品
            </a>
          </li>
          <li>
            <a href="/about" className="nav-link">
              关于
            </a>
          </li>
          <li>
            <a href="/contact" className="nav-link">
              联系
            </a>
          </li>
          <li className="purchase-link">
            <div style={{ position: "relative" }}>
              {/* 购物车图标 */}
              <svg
                style={{ width: "24px", height: "24px" }}
                viewBox="0 0 24 24"
              >
                <path
                  d="M17,18C15.89,18 15,18.89 15,20A2,2 0 0,0 17,22A2,2 0 0,0 19,20C19,18.89 18.1,18 17,18M1,2V4H3L6.6,11.59L5.24,14.04C5.09,14.32 5,14.65 5,15A2,2 0 0,0 7,17H19V15H7.42A0.25,0.25 0 0,1 7.17,14.75C7.17,14.7 7.18,14.66 7.2,14.63L8.1,13H15.55C16.3,13 16.96,12.58 17.3,11.97L20.88,5.5C20.95,5.34 21,5.17 21,5A1,1 0 0,0 20,4H5.21L4.27,2M7,18C5.89,18 5,18.89 5,20A2,2 0 0,0 7,22A2,2 0 0,0 9,20C9,18.89 8.1,18 7,18Z"
                  fill="#000"
                />
              </svg>

              {/* 红色标记 */}
              <div className="purchase-red">
                <span className="purchase-span">{purchase}</span>
              </div>
            </div>
          </li>
        </ul>
      </nav>

      {/* 内容部分 - 添加顶部内边距以避免被固定导航栏遮挡 */}
      <div style={{ paddingTop: isScrolled ? "200px" : "300px" }}>
        {/* 顶部个人介绍 */}
        <section
          style={{
            display: "flex",
            alignItems: "center",
            padding: "40px 20px",
            maxWidth: "1200px",
            margin: "0 auto",
          }}
        >
          <div className="image-card" style={{ flex: 1 }}>
            <div className="image-container">
              <a href="/about">
                <EnhancedImage
                  primarySrc="https://photoproject.oss-cn-wuhan-lr.aliyuncs.com/public/homeimage1.jpg"
                  fallbackSrc="https://photoproject.oss-cn-wuhan-lr.aliyuncs.com/public/homeimage1.jpg" // 静态图片使用相同URL
                  alt="223"
                />
              </a>
            </div>
          </div>
          <div style={{ flex: 1, paddingLeft: "40px" }}>
            <h1 className="upline">我是223</h1>
            <p className="downline">一名自由接案摄影师</p>
          </div>
        </section>

        <section
          style={{
            display: "flex",
            alignItems: "center",
            padding: "0px 20px",
            maxWidth: "1200px",
            margin: "0 auto",
          }}
        >
          <div style={{ flex: 1 }}>
            <h1 className="upline">LightRoom调色档</h1>
            <p className="downline">只需一个按键</p>
            <p className="downline">让你的照片瞬间提升质感</p>
            <a href="https://www.jjjason.com/lightroom">
              <p className="herfstyle">SHOP PERSETS</p>
            </a>
          </div>
          <div className="image-card" style={{ flex: 1 }}>
            <div className="image-container">
              <a href="https://www.jjjason.com/lightroom">
                <EnhancedImage
                  primarySrc="https://photoproject.oss-cn-wuhan-lr.aliyuncs.com/public/homeimage2.png"
                  fallbackSrc="https://photoproject.oss-cn-wuhan-lr.aliyuncs.com/public/homeimage2.png"
                  alt="lightroom"
                />
              </a>
            </div>
          </div>
        </section>

        <section
          style={{
            display: "flex",
            alignItems: "center",
            padding: "40px 20px",
            maxWidth: "1200px",
            margin: "0 auto",
          }}
        >
          <div className="image-card" style={{ flex: 1 }}>
            <div className="image-container">
              <a href="https://www.ysjf.com/material">
                <EnhancedImage
                  primarySrc="https://photoproject.oss-cn-wuhan-lr.aliyuncs.com/public/homeimage3.png"
                  fallbackSrc="https://photoproject.oss-cn-wuhan-lr.aliyuncs.com/public/homeimage3.png"
                  alt="3"
                />
              </a>
            </div>
          </div>
          <div style={{ flex: 1, paddingLeft: "40px" }}>
            <h1 className="upline">影片调色档</h1>
            <p className="downline">怎么样都调不出理想的颜色？</p>
            <p className="downline">你可以试试看这个</p>
            <a href="https://www.ysjf.com/material">
              <p className="herfstyle">SHOP PERSETS</p>
            </a>
          </div>
        </section>

        <section
          style={{
            backgroundColor: "#000", // 纯黑色背景
            color: "#fff",
            padding: "80px 20px 120px", // 增加底部内边距给版权信息留空间
            position: "relative",
          }}
        >
          <div
            style={{
              maxWidth: "1200px",
              margin: "0 auto",
              display: "flex",
              flexDirection: "column", // 改为垂直布局
              alignItems: "center", // 内容居中
              gap: "60px", // 增加垂直间距
            }}
          >
            {/* WORK 区块 - 在上方 */}
            <div style={{ width: "100%" }}>
              <a href="/works">
                <h2 className="herfstyle1">WORK</h2>
              </a>
              <div
                style={{
                  display: "flex", // 改为flex布局
                  flexWrap: "wrap", // 允许换行
                  justifyContent: "center", // 居中对齐
                  gap: "30px",
                  width: "100%",
                }}
              >
                {photos.map((photo) => (
                  <div
                    key={photo.id}
                    style={{
                      height: "300px", // 增加高度
                      width: "400px", // 设置宽度
                      borderRadius: "10px",
                    }}
                  >
                    <EnhancedImage
                      primarySrc={photo.url}
                      fallbackSrc={photo.originalUrl}
                      alt={`Photo ${photo.id}`}
                      style={{
                        width: "100%",
                        height: "100%",
                        objectFit: "cover", // 保持比例，填充容器
                        display: "block",
                      }}
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* 新增视频部分 */}
            <div style={{ width: "100%", marginTop: "40px" }}>
              <a href="https://www.bilibili.com/video/BV1qZqPYgEtc/?spm_id_from=333.1387.homepage.video_card.click">
                <h2 className="herfstyle1">LATEST PROJECT</h2>
              </a>

              <div style={{ display: "flex", justifyContent: "center" }}>
                <video
                  controls
                  width="800"
                  height="450"
                  poster="
https://photoproject.oss-cn-wuhan-lr.aliyuncs.com/public/poster.jpg"
                >
                  <source
                    src="https://photoproject.oss-cn-wuhan-lr.aliyuncs.com/workvideo.mp4"
                    type="video/mp4"
                  />
                  抱歉，您的浏览器不支持视频播放。
                </video>
              </div>
              <p style={{ textAlign: "center", marginTop: "20px" }}>
                看看我最新的摄影集锦
              </p>
            </div>

            {/* CONTACT 区块 - 在下方 */}
            <div
              style={{
                width: "100%",
                display: "flex",
                flexDirection: "column",
                alignItems: "center", // 内容居中
              }}
            >
              <a href="/contact">
                <h2 className="herfstyle1">CONTACT</h2>
              </a>
              <div
                style={{
                  display: "flex",
                  gap: "10px", // 增加图标间距
                }}
              >
                {/* Bilibili 图标 */}
                <a
                  href="https://space.bilibili.com/1663704071?spm_id_from=333.1007.0.0"
                  style={{ display: "block" }}
                >
                  <EnhancedImage
                    primarySrc="https://photoproject.oss-cn-wuhan-lr.aliyuncs.com/public/bilibili.png"
                    fallbackSrc="https://photoproject.oss-cn-wuhan-lr.aliyuncs.com/public/bilibili.png"
                    alt="bilibili"
                    className="iconstyle"
                  />
                </a>
                {/* github 图标 */}
                <a
                  href="https://github.com/223nobody"
                  style={{ display: "block" }}
                >
                  <EnhancedImage
                    primarySrc="https://photoproject.oss-cn-wuhan-lr.aliyuncs.com/public/github.png"
                    fallbackSrc="https://photoproject.oss-cn-wuhan-lr.aliyuncs.com/public/github.png"
                    alt="github"
                    className="iconstyle"
                  />
                </a>
                {/* ins 图标 */}
                <a
                  href="https://www.instagram.com"
                  style={{ display: "block" }}
                >
                  <EnhancedImage
                    primarySrc="https://photoproject.oss-cn-wuhan-lr.aliyuncs.com/public/instagram.png"
                    fallbackSrc="https://photoproject.oss-cn-wuhan-lr.aliyuncs.com/public/instagram.png"
                    alt="instagram"
                    className="iconstyle"
                  />
                </a>

                {/* YouTube 图标 */}
                <a href="https://youtube.com" style={{ display: "block" }}>
                  <EnhancedImage
                    primarySrc="https://photoproject.oss-cn-wuhan-lr.aliyuncs.com/public/youtube.png"
                    fallbackSrc="https://photoproject.oss-cn-wuhan-lr.aliyuncs.com/public/youtube.png"
                    alt="youtube"
                    className="iconstyle"
                  />
                </a>
              </div>

              <div
                style={{
                  textAlign: "center", // 文本居中
                  marginTop: "30px", // 增加顶部间距
                }}
              >
                <p>电话: +86 15972901567</p>
                <p style={{ marginTop: "10px" }}>邮箱: byfukun@foxmail.com</p>
              </div>
            </div>
          </div>

          {/* 版权信息 - 新增 */}
          <div className="copyright">©2025 - 223nobody</div>
        </section>
      </div>
      <div style={{ overflow: "auto" }}></div>
    </div>
  );
};

export default HomePage;
