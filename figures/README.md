# Academic Manuscript Figures

## 📊 Publication-Quality Figures for AI Investment Research

This directory contains 6 publication-ready figures for the academic manuscript:
**"AI Investment and Firm Productivity: Causal Evidence and Mechanism Decomposition from Japanese Enterprise Data"**

### 🎯 **Quick Access to Figures**

| Figure | Description | SVG File | Raw Download |
|--------|-------------|----------|--------------|
| **Figure 1** | Causal Effect (Main Results) | [View](figure1_main_results.svg) | [Download](https://raw.githubusercontent.com/Tatsuru-Kikuchi/AI-Investment-CEO/main/figures/figure1_main_results.svg) |
| **Figure 2** | Mechanism Decomposition | [View](figure2_mechanism_decomposition.svg) | [Download](https://raw.githubusercontent.com/Tatsuru-Kikuchi/AI-Investment-CEO/main/figures/figure2_mechanism_decomposition.svg) |
| **Figure 3** | Time Series Evolution | [View](figure3_time_series.svg) | [Download](https://raw.githubusercontent.com/Tatsuru-Kikuchi/AI-Investment-CEO/main/figures/figure3_time_series.svg) |
| **Figure 4** | Industry Heterogeneity | [View](figure4_industry_heterogeneity.svg) | [Download](https://raw.githubusercontent.com/Tatsuru-Kikuchi/AI-Investment-CEO/main/figures/figure4_industry_heterogeneity.svg) |
| **Figure 5** | Aggregate GDP Impact | [View](figure5_aggregate_impact.svg) | [Download](https://raw.githubusercontent.com/Tatsuru-Kikuchi/AI-Investment-CEO/main/figures/figure5_aggregate_impact.svg) |
| **Figure 6** | First Stage Results | [View](figure6_first_stage.svg) | [Download](https://raw.githubusercontent.com/Tatsuru-Kikuchi/AI-Investment-CEO/main/figures/figure6_first_stage.svg) |

### 📥 **Converting SVG to PNG**

#### **Method 1: Online Converter (Recommended)**
1. Visit [convertio.co/svg-png](https://convertio.co/svg-png/) or [cloudconvert.com/svg-to-png](https://cloudconvert.com/svg-to-png)
2. Click the "Raw Download" links above to save SVG files
3. Upload SVG files to the converter
4. Set **300 DPI** for publication quality
5. Download the PNG files

#### **Method 2: Browser Right-Click**
1. Click "View" links above to open SVG in browser
2. Right-click → "Save image as..." → Choose PNG format
3. Or screenshot for quick preview versions

#### **Method 3: Command Line (ImageMagick)**
```bash
# Install ImageMagick, then:
convert -density 300 figure1_main_results.svg figure1_main_results.png
convert -density 300 figure2_mechanism_decomposition.svg figure2_mechanism_decomposition.png
# ... repeat for all figures
```

### 📝 **LaTeX Integration**

Once you have PNG files, include them in your manuscript:

```latex
\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\textwidth]{figures/figure1_main_results.png}
    \caption{Causal Effect of AI Investment on Total Factor Productivity}
    \label{fig:main_results}
\end{figure}
```

**Recommended LaTeX settings:**
- **Resolution:** 300 DPI minimum
- **Width:** `0.8\textwidth` for readability
- **Placement:** `[H]` for exact positioning
- **Format:** PNG (recommended) or PDF

### 🎯 **Figure Details**

#### **Figure 1: Main Results**
- Shows 2.4% causal productivity effect
- Compares OLS vs IV estimates  
- Error bars with significance levels

#### **Figure 2: Mechanism Decomposition**
- Cost Reduction: 40% of total effect
- Revenue Enhancement: 35% of total effect
- Innovation Acceleration: 25% of total effect

#### **Figure 3: Time Series**
- AI adoption growth 2018-2023 (8% → 35%)
- Stable 2.4% productivity premium over time

#### **Figure 4: Industry Analysis**
- Manufacturing: 3.1% effect
- Professional Services: 2.8%
- Retail: 2.3%
- Finance: 2.1% 
- Construction: 1.7%

#### **Figure 5: Aggregate Impact**
- Current (15% adoption): ¥172B GDP impact
- Universal (90% adoption): ¥1.15T GDP impact

#### **Figure 6: First Stage**
- CEO age: -1.5% effect on AI investment
- Technical education: +22.3% effect
- Technology experience: +16.2% effect
- F-statistic: 24.7 (strong instruments)

### 📊 **Technical Specifications**

- **Format:** Scalable Vector Graphics (SVG)
- **Font:** Times New Roman (academic standard)
- **Size:** Optimized for journal submission
- **Quality:** Publication-ready with proper annotations
- **Style:** Professional academic formatting

### 🔗 **Repository Links**

- **Main Repository:** https://github.com/Tatsuru-Kikuchi/AI-Investment-CEO
- **Live Dashboards:** https://tatsuru-kikuchi.github.io/AI-Investment-CEO/
- **Contact:** tatsuru.kikuchi@gmail.com

### 📋 **Usage Notes**

All figures follow academic journal standards:
- Clear titles and axis labels
- Statistical significance indicators
- Comprehensive notes sections
- Error bars and confidence intervals
- Professional color schemes

Perfect for submission to:
- American Economic Review (AER)
- Management Science
- Journal of Political Economy
- Review of Economic Studies
- Other top-tier economics/management journals

---

**Generated:** August 2025 | **Version:** 1.0 | **Status:** Publication Ready