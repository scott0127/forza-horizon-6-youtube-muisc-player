# Forza Data Out (UDP Telemetry) 官方完整數據結構文件 (V2 Dash Format)

這份文件記錄了 Turn 10 Studios 官方公開的完整 UDP Data Out 封包結構。
Forza Horizon 4/5/6 以及新版 Forza Motorsport 皆預設使用 **V2 (Dash) 格式**，封包長度為 **324 bytes** (在某些舊版可能為 311 bytes，差額通常為結尾的未知/保留位元組)。

所有資料皆以 **Little-endian (小端序)** 進行編碼。

## 📦 完整封包欄位對照表 (Full Packet Structure)

| 偏移量 (Byte) | 長度 | 資料類型 | 變數名稱 (Variable Name) | 單位/說明 (Description) |
| :--- | :--- | :--- | :--- | :--- |
| **0** | 4 | `s32` | `IsRaceOn` | 1 = 駕駛中, 0 = 選單或暫停 |
| **4** | 4 | `u32` | `TimestampMS` | 遊戲時間戳 (毫秒) |
| **8** | 4 | `f32` | `EngineMaxRpm` | 引擎紅線區最高轉速 |
| **12** | 4 | `f32` | `EngineIdleRpm` | 引擎怠速轉速 |
| **16** | 4 | `f32` | `CurrentEngineRpm` | 當前引擎轉速 |
| **20** | 4 | `f32` | `AccelerationX` | X軸加速度 (Right) |
| **24** | 4 | `f32` | `AccelerationY` | Y軸加速度 (Up) |
| **28** | 4 | `f32` | `AccelerationZ` | Z軸加速度 (Forward) |
| **32** | 4 | `f32` | `VelocityX` | X軸速度 (Right) |
| **36** | 4 | `f32` | `VelocityY` | Y軸速度 (Up) |
| **40** | 4 | `f32` | `VelocityZ` | Z軸速度 (Forward) |
| **44** | 4 | `f32` | `AngularVelocityX` | 俯仰角速度 (Pitch) |
| **48** | 4 | `f32` | `AngularVelocityY` | 偏航角速度 (Yaw) |
| **52** | 4 | `f32` | `AngularVelocityZ` | 翻滾角速度 (Roll) |
| **56** | 4 | `f32` | `Yaw` | 偏航角 |
| **60** | 4 | `f32` | `Pitch` | 俯仰角 |
| **64** | 4 | `f32` | `Roll` | 翻滾角 |
| **68** | 4 | `f32` | `NormSuspensionTravelFrontLeft` | 左前避震壓縮比 (0.0=觸底, 1.0=完全伸展) |
| **72** | 4 | `f32` | `NormSuspensionTravelFrontRight` | 右前避震壓縮比 |
| **76** | 4 | `f32` | `NormSuspensionTravelRearLeft` | 左後避震壓縮比 |
| **80** | 4 | `f32` | `NormSuspensionTravelRearRight` | 右後避震壓縮比 |
| **84** | 4 | `f32` | `TireSlipRatioFrontLeft` | 左前輪縱向打滑率 (燒胎/鎖死) |
| **88** | 4 | `f32` | `TireSlipRatioFrontRight` | 右前輪縱向打滑率 |
| **92** | 4 | `f32` | `TireSlipRatioRearLeft` | 左後輪縱向打滑率 |
| **96** | 4 | `f32` | `TireSlipRatioRearRight` | 右後輪縱向打滑率 |
| **100** | 4 | `f32` | `WheelRotationSpeedFrontLeft` | 左前輪旋轉速度 (弧度/秒) |
| **104** | 4 | `f32` | `WheelRotationSpeedFrontRight` | 右前輪旋轉速度 |
| **108** | 4 | `f32` | `WheelRotationSpeedRearLeft` | 左後輪旋轉速度 |
| **112** | 4 | `f32` | `WheelRotationSpeedRearRight` | 右後輪旋轉速度 |
| **116** | 4 | `f32` | `WheelOnRumbleStripFrontLeft` | 左前輪壓到路緣石 (1=有, 0=無) |
| **120** | 4 | `f32` | `WheelOnRumbleStripFrontRight` | 右前輪壓到路緣石 |
| **124** | 4 | `f32` | `WheelOnRumbleStripRearLeft` | 左後輪壓到路緣石 |
| **128** | 4 | `f32` | `WheelOnRumbleStripRearRight` | 右後輪壓到路緣石 |
| **132** | 4 | `f32` | `WheelInPuddleDepthFrontLeft` | 左前輪水坑深度 (壓到水坑) |
| **136** | 4 | `f32` | `WheelInPuddleDepthFrontRight` | 右前輪水坑深度 |
| **140** | 4 | `f32` | `WheelInPuddleDepthRearLeft` | 左後輪水坑深度 |
| **144** | 4 | `f32` | `WheelInPuddleDepthRearRight` | 右後輪水坑深度 |
| **148** | 4 | `f32` | `SurfaceRumbleFrontLeft` | 左前輪路面震動反饋 |
| **152** | 4 | `f32` | `SurfaceRumbleFrontRight` | 右前輪路面震動反饋 |
| **156** | 4 | `f32` | `SurfaceRumbleRearLeft` | 左後輪路面震動反饋 |
| **160** | 4 | `f32` | `SurfaceRumbleRearRight` | 右後輪路面震動反饋 |
| **164** | 4 | `f32` | `TireSlipAngleFrontLeft` | 左前輪橫向打滑角 (甩尾/側滑) |
| **168** | 4 | `f32` | `TireSlipAngleFrontRight` | 右前輪橫向打滑角 |
| **172** | 4 | `f32` | `TireSlipAngleRearLeft` | 左後輪橫向打滑角 |
| **176** | 4 | `f32` | `TireSlipAngleRearRight` | 右後輪橫向打滑角 |
| **180** | 4 | `f32` | `TireCombinedSlipFrontLeft` | 左前輪綜合打滑值 |
| **184** | 4 | `f32` | `TireCombinedSlipFrontRight` | 右前輪綜合打滑值 |
| **188** | 4 | `f32` | `TireCombinedSlipRearLeft` | 左後輪綜合打滑值 |
| **192** | 4 | `f32` | `TireCombinedSlipRearRight` | 右後輪綜合打滑值 |
| **196** | 4 | `f32` | `SuspensionTravelMetersFrontLeft`| 左前避震器壓縮距離 (公尺) |
| **200** | 4 | `f32` | `SuspensionTravelMetersFrontRight`| 右前避震器壓縮距離 (公尺) |
| **204** | 4 | `f32` | `SuspensionTravelMetersRearLeft` | 左後避震器壓縮距離 (公尺) |
| **208** | 4 | `f32` | `SuspensionTravelMetersRearRight`| 右後避震器壓縮距離 (公尺) |
| **212** | 4 | `s32` | `CarOrdinal` | 車輛唯一 ID 編號 |
| **216** | 4 | `s32` | `CarClass` | 車輛分級 (0=E, 1=D, 2=C, 3=B, 4=A, 5=S1, 6=S2, 7=X) |
| **220** | 4 | `s32` | `CarPerformanceIndex` | 性能分數 (PI) |
| **224** | 4 | `s32` | `DrivetrainType` | 驅動方式 (0=FWD, 1=RWD, 2=AWD) |
| **228** | 4 | `s32` | `NumCylinders` | 引擎汽缸數量 |

*(--- 以上 232 Bytes 為早期 V1 格式，以下為 V2 Dash 擴充格式 ---)*

| 偏移量 (Byte) | 長度 | 資料類型 | 變數名稱 (Variable Name) | 單位/說明 (Description) |
| :--- | :--- | :--- | :--- | :--- |
| **232** | 4 | `f32` | `PositionX` | 世界地圖 X 座標 |
| **236** | 4 | `f32` | `PositionY` | 世界地圖 Y 座標 |
| **240** | 4 | `f32` | `PositionZ` | 世界地圖 Z 座標 |
| **244** | 4 | `f32` | `Speed` | 當前時速 (公尺/秒) *乘以 3.6 轉換為 km/h* |
| **248** | 4 | `f32` | `Power` | 引擎馬力輸出 (Watts) *除以 745.7 轉換為 HP* |
| **252** | 4 | `f32` | `Torque` | 引擎扭力輸出 (Newton Meters) |
| **256** | 4 | `f32` | `TireTempFrontLeft` | 左前輪胎溫 |
| **260** | 4 | `f32` | `TireTempFrontRight` | 右前輪胎溫 |
| **264** | 4 | `f32` | `TireTempRearLeft` | 左後輪胎溫 |
| **268** | 4 | `f32` | `TireTempRearRight` | 右後輪胎溫 |
| **272** | 4 | `f32` | `Boost` | 渦輪增壓值 (PSI 或 Bar) |
| **276** | 4 | `f32` | `Fuel` | 剩餘油量百分比 |
| **280** | 4 | `f32` | `DistanceTraveled` | 已行駛距離 |
| **284** | 4 | `f32` | `BestLap` | 最佳單圈時間 (秒) |
| **288** | 4 | `f32` | `LastLap` | 上一圈時間 (秒) |
| **292** | 4 | `f32` | `CurrentLap` | 當前單圈時間 (秒) |
| **296** | 4 | `f32` | `CurrentRaceTime` | 當前比賽總時間 (秒) |
| **300** | 2 | `u16` | `LapNumber` | 當前圈數 |
| **302** | 1 | `u8` | `RacePosition` | 目前比賽排名 |
| **303** | 1 | `u8` | `Accel` | 油門踩踏深度 (0 - 255) |
| **304** | 1 | `u8` | `Brake` | 煞車踩踏深度 (0 - 255) |
| **305** | 1 | `u8` | `Clutch` | 離合器踩踏深度 (0 - 255) |
| **306** | 1 | `u8` | `HandBrake` | 手煞車踩踏深度 (0 - 255) |
| **307** | 1 | `u8` | `Gear` | 當前檔位 (0=倒車, 1-10=前進檔位) |
| **308** | 1 | `s8` | `Steer` | 方向盤轉角 (-127 左 ~ +127 右) |
| **309** | 1 | `s8` | `NormalizedDrivingLine` | 行車線輔助偏離度 |
| **310** | 1 | `s8` | `NormalizedAIBrakeDiff` | AI 煞車差異度 |
| **311-323**|13 | *(保留)*| `Unknown/Padding` | 未知或對齊用的保留位元組 |

---
*備註：在 Python 中解析時，可以利用 `struct` 模組的 offset (如 `unpack_from('<f', data, 244)`) 精準抓出單一變數，不需要一次全部解碼，能大幅提升效能。*
