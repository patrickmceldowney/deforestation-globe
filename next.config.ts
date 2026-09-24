import type { NextConfig } from "next";
import CopyPlugin from "copy-webpack-plugin";
import path from "path";

const nextConfig: NextConfig = {
  webpack: (config) => {
    config.plugins.push(
      new CopyPlugin({
        patterns: [
          {
            from: path.join(
              process.cwd(),
              "node_modules/cesium/Build/Cesium/Workers"
            ),
            to: "static/Cesium/Workers",
          },
          {
            from: path.join(
              process.cwd(),
              "node_modules/cesium/Build/Cesium/ThirdParty"
            ),
            to: "static/Cesium/ThirdParty",
          },
          {
            from: path.join(
              process.cwd(),
              "node_modules/cesium/Build/Cesium/Assets"
            ),
            to: "static/Cesium/Assets",
          },
          {
            from: path.join(
              process.cwd(),
              "node_modules/cesium/Build/Cesium/Widgets"
            ),
            to: "static/Cesium/Widgets",
          },
        ],
      })
    );

    return config;
  },
};

export default nextConfig;
