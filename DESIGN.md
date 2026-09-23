# DESIGN — Optical Metrology Tools

> 這份是給外人看的架構說明,**會進 git、會被公開**。⛔ 不要寫個人或公司的事。

## 它在解什麼問題

量測儀器吐出來的是一堆原始數據,而工程師要的是「這批做得好不好」。
中間那段(去重複、排離群、算製程能力、挑分布、出報告)每次都要重做一遍,
而且商業統計軟體很貴。這支工具把那一段自動化。

## 三層

```
app/                進入點。三個版本:完整版、純 Python 版、JMP 版
 └─ src/ui/         畫面(tkinter)。每個對話框一個檔
     └─ src/core/   算的部分,⛔ 不碰畫面
         · pc_calculator          製程能力 Ppk / Cpk
         · aicc_calculator        用 AICc 挑最適分布
         · data_processor         讀檔、去重複、排離群
         · box_plot_analyzer      盒鬚圖
         · correlation_analyzer   相關性與迴歸
     └─ src/io/     讀寫檔、產 JSL、出 Excel
     └─ src/utils/  路徑、常數、版本;jmptools 是第三方(MIT)
scripts/jsl/        JMP 腳本樣板。工具產出 JSL,使用者貼進 JMP 跑
config/             變數預設組合(範例值)
```

## 幾個刻意的決定

**① 算的跟畫的分開。** `src/core/` 底下任何一支都可以單獨 import 來跑,不需要開視窗。
這樣才測得動,也才能之後接命令列。

**② 不直接讀 `.jmp` 二進位檔。** 那個格式沒有公開規格,靠猜位元組去解析,
換一個 JMP 版本就會錯,而且錯了不會報錯 —— 它會給你一組看起來合理的數字。
**所以流程是:在 JMP 裡匯出 CSV 或 Excel,工具讀那個。** 少一步,但結果是對的。

**③ 規格上下限由使用者提供,程式不預設。** 規格是各家自己訂的,
寫死在程式裡既不通用,也等於把別人的驗收標準印在原始碼上。
匯入格式:一張表,欄位 `Variable` / `LSL` / `USL` / `Target` / `Show Limits`。

**④ JMP 整合走「產腳本」不走「呼叫 API」。** JMP 沒有穩定的跨平台自動化介面,
產出 JSL 讓使用者自己貼進去跑,反而每一版都能用。

## 資料不進 git

`test_data/`、`docs/`、根目錄的 `*.xlsx`、`temp/`、`dist/`、`build/` 都被排除。
真實量測資料留在本機,repo 裡只有程式。
