import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import warnings
import os

warnings.filterwarnings('ignore')


class ManualMatrixAHP:
    def __init__(self, file_paths, indicator_names, comparison_matrix):
        self.file_paths = file_paths
        self.indicator_names = indicator_names
        self.comparison_matrix = comparison_matrix

    def load_and_merge_data(self):
        """Load and merge data from multiple Excel files"""
        print("Loading data...")
        all_data = {}

        # Read the first file to get city names and years
        first_df = pd.read_excel(self.file_paths[0], index_col=0)
        self.cities = first_df.columns.tolist()  # Column names are city names
        self.years = first_df.index.tolist()  # Row indices are years

        print(f"Found {len(self.cities)} cities: {self.cities}")
        print(f"Found {len(self.years)} years: {self.years}")
        # DEBUG: Confirm data orientation (Rows=Years, Columns=Cities)
        print(f"DEBUG: First 5 Cities (Columns): {self.cities[:5]}")
        print(f"DEBUG: First 5 Years (Rows/Index): {self.years[:5]}")

        for i, file_path in enumerate(self.file_paths):
            print(f"Loading file: {file_path} - Indicator: {self.indicator_names[i]}")

            try:
                # Read Excel file
                df = pd.read_excel(file_path, index_col=0)

                # Validate data format
                if not all(df.columns == self.cities):
                    print(f"Warning: City names in {self.indicator_names[i]} do not match. Adjusting...")
                    df = df[self.cities]  # Rearrange column order

                # Store data
                indicator_data = {}
                for city in self.cities:
                    city_values = df[city].values
                    indicator_data[city] = city_values

                all_data[self.indicator_names[i]] = indicator_data

            except Exception as e:
                print(f"Error loading file {file_path}: {e}")
                return None

        # Restructure data: {city: {indicator: data}}
        merged_data = {}
        for city in self.cities:
            city_data = {}
            for indicator in self.indicator_names:
                city_data[indicator] = all_data[indicator][city]
            merged_data[city] = city_data

        print(f"✅ Data loading complete: {len(self.cities)} cities, {len(self.indicator_names)} indicators, {len(self.years)} years of data")
        return merged_data

    def normalize_data(self, data, directions=None):
        """Normalize data"""
        if directions is None:
            # 默认所有指标都是正向
            directions = {indicator: 'pasitive' for indicator in self.indicator_names}  # 保持pasitive不变

        normalized_data = {}

        for city, city_data in data.items():
            normalized_city_data = {}
            for indicator, values in city_data.items():
                values = np.array(values)

                if directions[indicator] == 'pasitive':  # 保持pasitive不变
                    # 正向指标：越大越好
                    scaler = MinMaxScaler()
                    normalized_values = scaler.fit_transform(values.reshape(-1, 1)).flatten()
                else:
                    # 负向指标：越小越好
                    scaler = MinMaxScaler()
                    normalized_values = 1 - scaler.fit_transform(values.reshape(-1, 1)).flatten()

                normalized_city_data[indicator] = normalized_values
            normalized_data[city] = normalized_city_data

        print("✅ Data normalization complete")
        return normalized_data

    def get_manual_comparison_matrix(self):
        """Return predefined consistency matrix"""
        print("\n" + "=" * 60)
        print("                  Using predefined consistency matrix")
        print("=" * 60)
        self._print_matrix(self.comparison_matrix, "Predefined Consistency Matrix")
        return self.comparison_matrix

    def calculate_weights_from_matrix(self, comparison_matrix):
        """从一致性矩阵计算权重"""
        n = len(self.indicator_names)

        # 计算权重 - 特征值法
        eigenvalues, eigenvectors = np.linalg.eig(comparison_matrix)
        max_eigenvalue_index = np.argmax(eigenvalues.real)
        weights = eigenvectors[:, max_eigenvalue_index].real
        weights = np.abs(weights)
        weights = weights / np.sum(weights)

        return weights

    def consistency_check(self, comparison_matrix, weights):
        """一致性检验"""
        n = len(self.indicator_names)

        # 计算最大特征值
        weighted_sum = np.dot(comparison_matrix, weights)
        lambda_max = np.mean(weighted_sum / weights)

        # 计算一致性指标
        CI = (lambda_max - n) / (n - 1)

        # 随机一致性指标
        RI_dict = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41}
        RI = RI_dict.get(n, 1.41)

        # 一致性比率
        CR = CI / RI

        return {
            'is_consistent': CR < 0.1,
            'CR': CR,
            'CI': CI,
            'lambda_max': lambda_max,
            'RI': RI
        }

    def analyze_with_manual_matrix(self, data):
        """Perform AHP analysis using predefined matrix"""
        print("\n" + "=" * 60)
        print("                  AHP Analysis (Predefined Matrix)")
        print("=" * 60)

        # 获取手动输入的矩阵
        comparison_matrix = self.get_manual_comparison_matrix()

        # 计算权重
        weights = self.calculate_weights_from_matrix(comparison_matrix)

        # 一致性检验
        consistency = self.consistency_check(comparison_matrix, weights)

        # 输出权重结果
        print(f"\n📊 AHP Weight Calculation Results:")
        print("-" * 50)
        for i, indicator in enumerate(self.indicator_names):
            print(f"  {indicator}: {weights[i]:.4f} ({weights[i] * 100:6.2f}%)")

        # 输出一致性检验结果
        print(f"\n✅ Consistency Check Results:")
        print(f"  Maximum Eigenvalue λ_max: {consistency['lambda_max']:.4f}")
        print(f"  Consistency Index CI: {consistency['CI']:.4f}")
        print(f"  Random Consistency Index RI: {consistency['RI']:.4f}")
        print(f"  Consistency Ratio CR: {consistency['CR']:.4f}")

        if consistency['is_consistent']:
            print(f"  🟢 Consistency Check: Passed (CR < 0.1)")
        else:
            print(f"  🟡 Consistency Check: Failed (CR >= 0.1). Consider adjusting the comparison matrix.")

        return {
            'weights': weights,
            'consistency': consistency,
            'comparison_matrix': comparison_matrix
        }

    def calculate_city_scores(self, data, weights):
        """Calculate overall scores for each city"""
        city_scores = {}

        print("\n" + "=" * 60)
        print("                  City Overall Score Calculation")
        print("=" * 60)

        # 计算每年的得分
        for year_idx, year in enumerate(self.years):
            year_scores = []
            for city in self.cities:
                city_score = 0
                for i, indicator in enumerate(self.indicator_names):
                    city_score += data[city][indicator][year_idx] * weights[i]
                year_scores.append(city_score)

            for i, city in enumerate(self.cities):
                if city not in city_scores:
                    city_scores[city] = []
                city_scores[city].append(year_scores[i])

        # 打印得分信息
        for city in self.cities:
            scores = city_scores[city]
            print(f"\n🏙️ {city}:")
            print(f"  Score Trend: {[f'{s:.4f}' for s in scores]}")
            print(f"  Average Score: {np.mean(scores):.4f}")
            print(f"  Score Growth: {scores[-1] - scores[0]:.4f}")

        return city_scores

    def plot_analysis_results(self, results, city_scores):
        """Plot analysis results"""
        plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

        # 1. Indicator Weights Bar Chart
        plt.figure(figsize=(8, 6))
        bars = plt.bar(self.indicator_names, results['weights'], color=['#ff6b6b', '#4ecdc4', '#45b7d1'])
        #plt.title('AHP Indicator Weights', fontsize=14, fontweight='bold')
        plt.ylabel('Weight', fontsize=14)
        plt.xticks(fontsize=14)
        for bar, weight in zip(bars, results['weights']):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2., height + 0.01, f'{weight:.3f}', ha='center', va='bottom', fontweight='bold')
        self._save_figure("ahp_indicator_weights.svg")
        plt.close()

        # 2. Indicator Weights Pie Chart
        plt.figure(figsize=(8, 6))
        plt.pie(results['weights'], labels=self.indicator_names, autopct='%1.1f%%', colors=['#ff9999', '#66b3ff', '#99ff99'], startangle=90)
        plt.title('Indicator Weight Distribution', fontsize=14, fontweight='bold')
        self._save_figure("indicator_weight_distribution.svg")
        plt.close()

        # 3. City Score Trends
        plt.figure(figsize=(8, 6))
        for city, scores in city_scores.items():
            plt.plot(self.years, scores, marker='s', label=city, linewidth=2)
        plt.title('City Overall Score Trends', fontsize=14, fontweight='bold')
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Overall Score', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        self._save_figure("city_score_trends.svg")
        plt.close()

        # 4. Final Year City Rankings
        plt.figure(figsize=(8, 6))
        final_scores = {city: scores[-1] for city, scores in city_scores.items()}
        ranked_cities = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        cities_rank = [item[0] for item in ranked_cities]
        scores_rank = [item[1] for item in ranked_cities]
        colors = plt.cm.viridis(np.linspace(0, 1, len(cities_rank)))
        bars = plt.barh(cities_rank, scores_rank, color=colors)
        plt.title(f'Final Year ({self.years[-1]}) City Rankings', fontsize=14, fontweight='bold')
        plt.xlabel('Overall Score', fontsize=12)
        for bar, score in zip(bars, scores_rank):
            plt.text(score + 0.01, bar.get_y() + bar.get_height() / 2, f'{score:.3f}', va='center', fontsize=10, fontweight='bold')
        self._save_figure("final_year_city_rankings.svg")
        plt.close()

    def plot_comparison_matrix_heatmap(self, comparison_matrix):
        """Plot comparison matrix heatmap"""
        plt.figure(figsize=(8, 6))
        sns.heatmap(comparison_matrix, annot=True, fmt='.3f', cmap='YlOrRd', xticklabels=self.indicator_names, yticklabels=self.indicator_names, cbar_kws={'label': 'Comparison Scale'})
        plt.title('AHP Comparison Matrix Heatmap', fontsize=14, fontweight='bold')
        plt.tight_layout()
        self._save_figure("ahp_comparison_matrix_heatmap.svg")
        plt.close()

    def plot_multiple_weights_comparison(self, weight_sets, matrix_names):
        """Plot comparison of weights from multiple matrices in a single bar chart"""
        plt.figure(figsize=(12, 8))
        
        n_indicators = len(self.indicator_names)
        n_matrices = len(matrix_names)
        
        # Set up bar width and positions
        bar_width = 0.8 / n_matrices
        index = np.arange(n_indicators)
        
        colors = plt.cm.get_cmap('tab10', n_matrices)
        
        for i, (name, weights) in enumerate(zip(matrix_names, weight_sets)):
            # Calculate bar positions
            bar_positions = index + i * bar_width - (n_matrices - 1) * bar_width / 2
            
            print(f"DEBUG: Plotting weights for {name}. bar_positions length: {len(bar_positions)}, weights length: {len(weights)}")
            
            bars = plt.bar(bar_positions, weights, bar_width, label=name, color=colors(i))
            
            # Add weight values on top of bars
            for bar, weight in zip(bars, weights):
                plt.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.005,
                         f'{weight:.3f}', ha='center', va='bottom', fontsize=8)

        plt.title('Comparison of AHP Weights from Different Matrices', fontsize=16, fontweight='bold')
        plt.xlabel('Indicators', fontsize=12)
        plt.ylabel('Weight', fontsize=12)
        plt.xticks(index, self.indicator_names, rotation=45, ha='right')
        plt.legend(title="Matrix", loc='upper left')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        self._save_figure("ahp_multiple_weights_comparison.svg")
        plt.close()

    def _save_figure(self, base_filename):
        """Save figure to the Figure/AHP directory with automatic numbering if needed"""
        figures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Output Files", "Figures", "AHP")
        os.makedirs(figures_dir, exist_ok=True)
        output_path = os.path.join(figures_dir, base_filename)
        counter = 1
        while os.path.exists(output_path):
            name, ext = os.path.splitext(base_filename)
            output_path = os.path.join(figures_dir, f"{name}_{counter}{ext}")
            counter += 1
        plt.savefig(output_path, format="svg", bbox_inches="tight")
        print(f"\n📊 Figure saved to: {output_path}")

    def export_results(self, results, city_scores, output_file='manual_ahp_results.xlsx'):
        """Export analysis results to Excel"""
        # 确保导出目录存在
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Output Files')
        os.makedirs(output_dir, exist_ok=True)

        # 检查文件名是否被占用，若被占用则自动编号
        base_name, ext = os.path.splitext(output_file)
        output_path = os.path.join(output_dir, output_file)
        # counter = 1
        # while os.path.exists(output_path):
        #     output_path = os.path.join(output_dir, f"{base_name}_{counter}{ext}")
        #     #output_path = os.path.join(output_dir, f"{base_name}{ext}")
        #     counter += 1

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 1. 综合权重
            weights_df = pd.DataFrame({
                '指标': self.indicator_names,
                '权重': results['weights'],
                '权重百分比': [f'{w * 100:.2f}%' for w in results['weights']]
            })
            weights_df.to_excel(writer, sheet_name='AHP权重', index=False)

            # 2. 一致性检验结果
            consistency_df = pd.DataFrame([{
                '最大特征值': results['consistency']['lambda_max'],
                '一致性指标CI': results['consistency']['CI'],
                '随机一致性指标RI': results['consistency']['RI'],
                '一致性比率CR': results['consistency']['CR'],
                '检验结果': '通过' if results['consistency']['is_consistent'] else '未通过'
            }])
            consistency_df.to_excel(writer, sheet_name='一致性检验', index=False)

            # 3. 比较矩阵
            matrix_df = pd.DataFrame(
                results['comparison_matrix'],
                index=self.indicator_names,
                columns=self.indicator_names
            )
            matrix_df.to_excel(writer, sheet_name='比较矩阵')

            # 4. 城市得分
            city_scores_data = []
            for city, scores in city_scores.items():
                row = {'城市': city}
                for year_idx, year in enumerate(self.years):
                    row[year] = scores[year_idx]
                city_scores_data.append(row)

            scores_df = pd.DataFrame(city_scores_data)
            scores_df.to_excel(writer, sheet_name='城市得分', index=False)

        print(f"\n📁 Analysis results exported to: {output_path}")

    def export_city_rankings(self, city_scores, output_file='ahp_city_rankings_results.xlsx'):
        """Export final year city rankings to Excel"""
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Output Files')
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, output_file)
        
        # Get final year scores and calculate average scores
        final_scores = {}
        average_scores = {}
        
        for city, scores in city_scores.items():
            final_scores[city] = scores[-1]
            average_scores[city] = np.mean(scores)
        
        # Create DataFrame for final scores and average scores
        ranking_data = []
        for city in self.cities:
            ranking_data.append({
                'City': city,
                'Final Score': final_scores[city],
                'Average Score': average_scores[city]
            })
        
        ranking_df = pd.DataFrame(ranking_data)
        
        # Calculate rank based on final score (higher score = lower rank number)
        ranking_df['Final Rank'] = ranking_df['Final Score'].rank(ascending=False, method='min').astype(int)
        
        # Calculate rank based on average score
        ranking_df['Average Rank'] = ranking_df['Average Score'].rank(ascending=False, method='min').astype(int)
        
        # Format scores
        ranking_df['Final Score'] = ranking_df['Final Score'].round(4)
        ranking_df['Average Score'] = ranking_df['Average Score'].round(4)

        # Sort by final rank
        ranking_df = ranking_df.sort_values(by='Final Rank')

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            ranking_df.to_excel(writer, sheet_name='City Rankings', index=False)

        print(f"\n📁 AHP city rankings exported to: {output_path}")

    def _print_matrix(self, matrix, title):
        """Print matrix"""
        print(f"\n{title}:")
        print(" " * 12, end="")
        for name in self.indicator_names:
            print(f"{name:>12}", end="")
        print()

        for i, row in enumerate(matrix):
            print(f"{self.indicator_names[i]:12}", end="")
            for val in row:
                print(f"{val:12.3f}", end="")
            print()

def matrixPrinter(FILE_PATHS, INDICATOR_NAMES, COMPARISON_MATRIX):
    ahp_analyzer = ManualMatrixAHP(FILE_PATHS, INDICATOR_NAMES, COMPARISON_MATRIX)

    # 加载数据
    data = ahp_analyzer.load_and_merge_data()

    if data is not None:
        # 数据标准化 - 保持pasitive不变
        directions = {
            'X1 (Waste)': 'pasitive',
            'X2 (Water)': 'pasitive',
            'X3 (Air)': 'pasitive',
            'X4 (Population)': 'pasitive',
            'X5 (Energy)': 'pasitive',
            'X6 (Transport)': 'pasitive',
            'X7 (Ecology)': 'pasitive',
            'X8 (Infrastructure)': 'positive'
        }
        normalized_data = ahp_analyzer.normalize_data(data, directions)

        # 使用预定义矩阵进行AHP分析
        results = ahp_analyzer.analyze_with_manual_matrix(normalized_data)

        # 计算城市得分
        city_scores = ahp_analyzer.calculate_city_scores(normalized_data, results['weights'])

        # 绘制图表
        ahp_analyzer.plot_analysis_results(results, city_scores)
        ahp_analyzer.plot_comparison_matrix_heatmap(results['comparison_matrix'])

        # 导出结果
        ahp_analyzer.export_results(results, city_scores)
        ahp_analyzer.export_city_rankings(city_scores)

        # 输出最终排名
        print("\n" + "=" * 60)
        print("                  Final City Rankings")
        print("=" * 60)
        final_scores = {city: scores[-1] for city, scores in city_scores.items()}
        ranked_cities = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)

        for rank, (city, score) in enumerate(ranked_cities, 1):
            print(f"🏆 Rank {rank}: {city} - Score: {score:.4f}")

        print(f"\n🎯 AHP Analysis Complete! Best City: {ranked_cities[0][0]}")


# 使用示例
if __name__ == "__main__":
    # 配置参数 - 请根据实际情况修改
    import os

    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 定义输入文件目录为 Operating/
    input_dir = os.path.join(current_dir, 'Operating')

    FILE_PATHS = [  
        os.path.join(input_dir, 'Solid_Waste.xlsx'),
        os.path.join(input_dir, 'Water_Use.xlsx'),
        os.path.join(input_dir, 'Air_Quality.xlsx'),
        os.path.join(input_dir, 'Population_Density.xlsx'),
        os.path.join(input_dir, 'Electricity_Generated.xlsx'),
        os.path.join(input_dir, 'Transport.xlsx'),
        os.path.join(input_dir, 'Greening_Impact_Index.xlsx'),
        os.path.join(input_dir, 'Have_Stadium.xlsx')
    ]

    INDICATOR_NAMES = ['X1 (Waste)', 'X2 (Water)', 'X3 (Air)', 'X4 (Population)', 'X5 (Energy)', 'X6 (Transport)', 'X7 (Ecology)', 'X8 (Infrastructure)']  # 替换为您的实际指标名称

    # 原来的矩阵----------------------------------
    # COMPARISON_MATRIX = np.array([
    #     [1.0000, 1.0000, 5.0000, 0.3333, 3.0000, 0.2000, 3.0000, 7.0000],
    #     [1.0000, 1.0000, 5.0000, 0.3333, 3.0000, 0.2000, 3.0000, 7.0000],
    #     [0.2000, 0.2000, 1.0000, 0.2000, 0.3333, 0.1429, 0.5000, 3.0000],
    #     [3.0000, 3.0000, 5.0000, 1.0000, 3.0000, 0.3333, 5.0000, 7.0000],
    #     [0.3333, 0.3333, 3.0000, 0.3333, 1.0000, 0.2000, 1.0000, 5.0000],
    #     [5.0000, 5.0000, 7.0000, 3.0000, 5.0000, 1.0000, 7.0000, 9.0000],
    #     [0.3333, 0.3333, 2.0000, 0.2000, 1.0000, 0.1429, 1.0000, 5.0000],
    #     [0.1429, 0.1429, 0.3333, 0.1429, 0.2000, 0.1111, 0.2000, 1.0000]
    # ])
#nononono
    # COMPARISON_MATRIX = np.array([
    #     [1.0000, 1.4565, 2.4495, 1.0746, 0.9036, 0.8633, 1.7321],
    #     [0.6866, 1.0000, 1.5651, 0.8801, 0.7598, 0.9036, 1.4565],
    #     [0.4082, 0.6389, 1.0000, 0.6223, 0.6043, 0.6043, 1.0000],
    #     [0.8190, 1.0000, 1.6069, 1.0000, 1.0466, 1.0466, 1.3512],
    #     [1.1067, 1.3161, 1.6549, 0.9554, 1.0000, 0.8409, 1.2574],
    #     [1.1583, 1.1067, 1.6549, 0.9554, 1.1892, 1.0000, 1.3296],
    #     [0.5774, 0.6866, 1.0000, 0.7401, 0.7953, 0.7521, 1.0000]
    # ])
#NFL no
    # COMPARISON_MATRIX = np.array([
    #     [1.0000, 1.0000, 0.3333, 3.0000, 1.5000, 3.0000, 2.0000, 1.5000],
    #     [1.0000, 1.0000, 0.3333, 3.0000, 1.5000, 3.0000, 2.0000, 1.5000],
    #     [3.0000, 3.0000, 1.0000, 5.0000, 3.0000, 5.0000, 3.0000, 3.0000],
    #     [0.3333, 0.3333, 0.2000, 1.0000, 0.7500, 1.5000, 0.7500, 0.6700],
    #     [0.6667, 0.6667, 0.3333, 1.3333, 1.0000, 2.0000, 1.5000, 0.8000],
    #     [0.3333, 0.3333, 0.2000, 0.6667, 0.5000, 1.0000, 0.6700, 0.8000],
    #     [0.5000, 0.5000, 0.3333, 1.3333, 0.6667, 1.4925, 1.0000, 0.8000],
    #     [0.6667, 0.6667, 0.3333, 1.4925, 1.2500, 1.2500, 1.2500, 1.0000]
    # ])
#NFL  no
    # COMPARISON_MATRIX = np.array([
    #     [1.0000, 1.3333, 0.6667, 1.5000, 0.6667, 0.3333, 2.0000, 0.8000],
    #     [0.7500, 1.0000, 0.3333, 0.7500, 0.3333, 0.2000, 1.5000, 0.6700],
    #     [1.5000, 3.0000, 1.0000, 2.0000, 1.0000, 0.3333, 3.0000, 1.5000],
    #     [0.6667, 1.3333, 0.5000, 1.0000, 0.5000, 0.3333, 1.4925, 0.8000],
    #     [1.5000, 3.0000, 1.0000, 2.0000, 1.0000, 0.3333, 3.0000, 1.5000],
    #     [3.0000, 5.0000, 3.0000, 3.0000, 3.0000, 1.0000, 5.0000, 3.0000],
    #     [0.5000, 0.6667, 0.3333, 0.6700, 0.3333, 0.2000, 1.0000, 0.8000],
    #     [1.2500, 1.4925, 0.6667, 1.2500, 0.6667, 0.3333, 1.2500, 1.0000]
    # ])
#Olympicssssssss
    # 原来的矩阵----------------------------------
    COMPARISON_MATRIX = np.array([
        [1.0000, 1.0000, 5.0000, 0.3333, 3.0000, 0.2000, 3.0000, 7.0000],
        [1.0000, 1.0000, 5.0000, 0.3333, 3.0000, 0.2000, 3.0000, 7.0000],
        [0.2000, 0.2000, 1.0000, 0.2000, 0.3333, 0.1429, 0.5000, 3.0000],
        [3.0000, 3.0000, 5.0000, 1.0000, 3.0000, 0.3333, 5.0000, 7.0000],
        [0.3333, 0.3333, 3.0000, 0.3333, 1.0000, 0.2000, 1.0000, 5.0000],
        [5.0000, 5.0000, 7.0000, 3.0000, 5.0000, 1.0000, 7.0000, 9.0000],
        [0.3333, 0.3333, 2.0000, 0.2000, 1.0000, 0.1429, 1.0000, 5.0000],
        [0.1429, 0.1429, 0.3333, 0.1429, 0.2000, 0.1111, 0.2000, 1.0000]
    ])

#用于敏感性分析的矩阵------------------------------

# #deepseek
#     COMPARISON_MATRIX = np.array([
#         [1.0000, 1.5000, 0.6667, 2.0000, 1.3333, 0.7500, 0.5000, 3.0000],
#         [0.6667, 1.0000, 0.5000, 1.5000, 1.0000, 0.6667, 0.4000, 2.0000],
#         [1.5000, 2.0000, 1.0000, 2.5000, 1.6667, 1.0000, 0.6667, 3.5000],
#         [0.5000, 0.6667, 0.4000, 1.0000, 0.6667, 0.5000, 0.3333, 1.5000],
#         [0.7500, 1.0000, 0.6000, 1.5000, 1.0000, 0.6667, 0.5000, 2.0000],
#         [1.3333, 1.5000, 1.0000, 2.0000, 1.5000, 1.0000, 0.6667, 2.5000],
#         [2.0000, 2.5000, 1.5000, 3.0000, 2.0000, 1.5000, 1.0000, 4.0000],
#         [0.3333, 0.5000, 0.2857, 0.6667, 0.5000, 0.4000, 0.2500, 1.0000]
#     ])
# #Gemini
#     COMPARISON_MATRIX2 = np.array([
#         [1.0000, 1.0000, 2.0000, 3.0000, 2.0000, 0.5000, 1.0000, 0.3333],
#         [1.0000, 1.0000, 2.0000, 3.0000, 2.0000, 0.5000, 1.0000, 0.3333],
#         [0.5000, 0.5000, 1.0000, 2.0000, 0.5000, 0.3333, 0.5000, 0.2000],
#         [0.3333, 0.3333, 0.5000, 1.0000, 0.3333, 0.2500, 0.3333, 0.2000],
#         [0.5000, 0.5000, 2.0000, 3.0000, 1.0000, 0.3333, 0.5000, 0.2500],
#         [2.0000, 2.0000, 3.0000, 4.0000, 3.0000, 1.0000, 2.0000, 0.5000],
#         [1.0000, 1.0000, 2.0000, 3.0000, 2.0000, 0.5000, 1.0000, 0.3333],
#         [3.0000, 3.0000, 5.0000, 5.0000, 4.0000, 2.0000, 3.0000, 1.0000]
#     ])
# #Grok
#     COMPARISON_MATRIX = np.array([
#         [1.0000, 2.0000, 3.0000, 1.5000, 0.5000, 1.0000, 0.3333, 2.0000],
#         [0.5000, 1.0000, 2.0000, 1.0000, 0.3333, 0.5000, 0.2000, 1.5000],
#         [0.3333, 0.5000, 1.0000, 0.6667, 0.2000, 0.3333, 0.1429, 1.0000],
#         [0.6667, 1.0000, 1.5000, 1.0000, 0.3333, 0.6667, 0.2500, 1.3333],
#         [2.0000, 3.0000, 5.0000, 3.0000, 1.0000, 2.0000, 0.6667, 4.0000],
#         [1.0000, 2.0000, 3.0000, 1.5000, 0.5000, 1.0000, 0.3333, 2.0000],
#         [3.0000, 5.0000, 7.0000, 4.0000, 1.5000, 3.0000, 1.0000, 5.0000],
#         [0.5000, 0.6667, 1.0000, 0.7500, 0.2500, 0.5000, 0.2000, 1.0000]
#     ])
# #ChatGPT
#     COMPARISON_MATRIX = np.array([
#         [1.0000, 0.4500, 0.2800, 0.2000, 0.1800, 0.1600, 0.1300, 0.1200],
#         [2.2222, 1.0000, 0.7000, 0.4800, 0.4000, 0.3500, 0.3000, 0.2800],
#         [3.5714, 1.4286, 1.0000, 0.7000, 0.5800, 0.5000, 0.4200, 0.3800],
#         [5.0000, 2.0833, 1.4286, 1.0000, 0.8500, 0.7000, 0.6000, 0.5300],
#         [5.5556, 2.5000, 1.7241, 1.1765, 1.0000, 0.8500, 0.7500, 0.6500],
#         [6.2500, 2.8571, 2.0000, 1.4286, 1.1765, 1.0000, 0.8800, 0.7500],
#         [7.6923, 3.3333, 2.3810, 1.6667, 1.3333, 1.1364, 1.0000, 0.8500],
#         [8.3333, 3.5714, 2.6316, 1.8868, 1.5385, 1.3333, 1.1765, 1.0000]
#     ])


    # 创建AHP分析器
    ahp_analyzer = ManualMatrixAHP(FILE_PATHS, INDICATOR_NAMES, COMPARISON_MATRIX)
    
    # 计算权重并比较多个矩阵
    matrices = {
        'COMPARISON_MATRIX': COMPARISON_MATRIX
    }
    
    weight_sets = []
    matrix_names = []
    
    print("\n" + "=" * 60)
    print("                  Calculating Weights for Multiple Matrices")
    print("=" * 60)
    
    for name, matrix in matrices.items():
        weights = ahp_analyzer.calculate_weights_from_matrix(matrix)
        weight_sets.append(weights)
        matrix_names.append(name)
        
        # 可选：打印所有矩阵的一致性检验
        consistency = ahp_analyzer.consistency_check(matrix, weights)
        print(f"\nMatrix: {name}")
        print(f"  CR: {consistency['CR']:.4f} ({'Passed' if consistency['is_consistent'] else 'Failed'})")
        
    # 绘制多矩阵权重对比图
    ahp_analyzer.plot_multiple_weights_comparison(weight_sets, matrix_names)
    
    # 使用COMPARISON_MATRIX运行主要分析
    matrixPrinter(FILE_PATHS, INDICATOR_NAMES, COMPARISON_MATRIX)