import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import warnings
import os

warnings.filterwarnings('ignore')


class CRITICAnalyzer:
    def __init__(self, file_paths, indicator_names):
        self.file_paths = file_paths
        self.indicator_names = indicator_names

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
            directions = {indicator: 'positive' for indicator in self.indicator_names}

        normalized_data = {}

        for city, city_data in data.items():
            normalized_city_data = {}
            for indicator, values in city_data.items():
                values = np.array(values)

                # 保持pasitive和positive不变
                if directions[indicator] in ['positive', 'pasitive']:
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

    def create_decision_matrix(self, data, year_idx=None):
        """创建决策矩阵
        year_idx: 指定年份索引，None表示使用所有年份数据
        """
        n_cities = len(self.cities)
        n_indicators = len(self.indicator_names)

        if year_idx is not None:
            # 单一年份的决策矩阵
            decision_matrix = np.zeros((n_cities, n_indicators))
            for i, city in enumerate(self.cities):
                for j, indicator in enumerate(self.indicator_names):
                    decision_matrix[i, j] = data[city][indicator][year_idx]
        else:
            # 所有年份平均值的决策矩阵
            decision_matrix = np.zeros((n_cities, n_indicators))
            for i, city in enumerate(self.cities):
                for j, indicator in enumerate(self.indicator_names):
                    decision_matrix[i, j] = np.mean(data[city][indicator])

        return decision_matrix

    def critic_method(self, decision_matrix):
        """CRITIC权重计算方法"""
        # 1. 数据标准化（已经标准化过，这里再次确保）
        X = decision_matrix.copy()

        # 2. 计算指标间的相关系数
        correlation_matrix = np.corrcoef(X, rowvar=False)

        # 3. 计算每个指标的标准差
        std_dev = np.std(X, axis=0)

        # 4. 计算每个指标的信息量
        information_amount = np.zeros(len(self.indicator_names))
        for j in range(len(self.indicator_names)):
            conflict = 0
            for k in range(len(self.indicator_names)):
                conflict += (1 - correlation_matrix[j, k])
            information_amount[j] = std_dev[j] * conflict

        # 5. 计算权重
        total_information = np.sum(information_amount)
        if total_information == 0:
            # If all indicators have zero information (e.g., all data points are the same),
            # assign equal weights to prevent division by zero (NaN weights).
            weights = np.ones(len(self.indicator_names)) / len(self.indicator_names)
        else:
            weights = information_amount / total_information

        results = {
            'weights': weights,
            'std_dev': std_dev,
            'correlation_matrix': correlation_matrix,
            'information_amount': information_amount
        }

        return results

    def analyze_overall_weights(self, data):
        """Analyze overall weights based on all years' data"""
        print("\n" + "=" * 60)
        print("                  CRITIC Method Overall Weight Analysis")
        print("=" * 60)

        # 使用所有年份的平均值创建决策矩阵
        decision_matrix = self.create_decision_matrix(data)

        # CRITIC权重计算
        results = self.critic_method(decision_matrix)

        print("\n📊 Indicator Statistics:")
        print("Indicator     Std Dev     Information     Weight")
        print("-" * 50)
        for i, indicator in enumerate(self.indicator_names):
            print(
                f"{indicator:8}  {results['std_dev'][i]:8.8f}  {results['information_amount'][i]:8.8f}  {results['weights'][i]:8.8f} ({results['weights'][i] * 100:6.2f}%)")

        return results

    def analyze_yearly_weights(self, data):
        """Analyze yearly weights"""
        print("\n" + "=" * 60)
        print("                  Yearly CRITIC Weight Analysis")
        print("=" * 60)

        yearly_results = {}

        for year_idx, year in enumerate(self.years):
            # 创建该年份的决策矩阵
            decision_matrix = self.create_decision_matrix(data, year_idx)

            # CRITIC权重计算
            results = self.critic_method(decision_matrix)

            yearly_results[year] = {
                'weights': results['weights'],
                'std_dev': results['std_dev'],
                'information_amount': results['information_amount']
            }

            print(f"\n📅 Weights for {year}:")
            for i, indicator in enumerate(self.indicator_names):
                print(f"  {indicator}: {results['weights'][i]:.8f} ({results['weights'][i] * 100:.2f}%)")

        return yearly_results

    def calculate_city_scores(self, data, weights):
        """计算各城市综合得分"""
        city_scores = {}

        print("\n" + "=" * 60)
        print("                  City Overall Score Calculation")
        print("=" * 60)

        # 计算每年的得分
        for year_idx, year in enumerate(self.years):
            decision_matrix = self.create_decision_matrix(data, year_idx)
            year_scores = np.dot(decision_matrix, weights)

            for i, city in enumerate(self.cities):
                if city not in city_scores:
                    city_scores[city] = []
                city_scores[city].append(year_scores[i])

        # 打印得分信息
        for city in self.cities:
            scores = city_scores[city]
            print(f"\n🏙️ {city}:")
            print(f"  Score Trend: {[f'{s:.8f}' for s in scores]}")
            print(f"  Average Score: {np.mean(scores):.8f}")
            print(f"  Score Growth: {scores[-1] - scores[0]:.8f}")

        return city_scores

    def plot_critic_analysis(self, overall_results, yearly_results, city_scores):
        """Plot CRITIC analysis results"""
        # Set font for English
        plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

        # 1. Indicator Weights Bar Chart
        plt.figure(figsize=(8, 6))
        bars = plt.bar(self.indicator_names, overall_results['weights'],
                       color=['#ff6b6b', '#4ecdc4', '#45b7d1'])
        plt.title('CRITIC Indicator Weights', fontsize=14, fontweight='bold')
        plt.ylabel('Weight', fontsize=12)
        plt.ylim(0, 0.5)
        for bar, weight in zip(bars, overall_results['weights']):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2., height + 0.01,
                     f'{weight:.8f}', ha='center', va='bottom', fontweight='bold')
        self._save_figure("critic_indicator_weights.svg")
        plt.close()

        # 2. Yearly Weight Changes
        plt.figure(figsize=(8, 6))
        years = list(yearly_results.keys())
        weights_data = {indicator: [] for indicator in self.indicator_names}
        for year in years:
            weights = yearly_results[year]['weights']
            for i, indicator in enumerate(self.indicator_names):
                weights_data[indicator].append(weights[i])
        for indicator in self.indicator_names:
            plt.plot(years, weights_data[indicator], marker='o', label=indicator, linewidth=2.5, markersize=6)
        plt.title('Yearly Weight Changes', fontsize=14, fontweight='bold')
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Weight', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tick_params(axis='x', rotation=45)
        self._save_figure("yearly_weight_changes.svg")
        plt.close()

        # 3. City Score Trends
        plt.figure(figsize=(8, 6))
        for city, scores in city_scores.items():
            plt.plot(years, scores, marker='s', label=city, linewidth=2)
        plt.title('City Overall Score Trends', fontsize=14, fontweight='bold')
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Overall Score', fontsize=12)
        plt.legend(loc='upper right')
        plt.grid(True, alpha=0.3)
        plt.tick_params(axis='x', rotation=45)
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
            plt.text(score + 0.01, bar.get_y() + bar.get_height() / 2,
                     f'{score:.8f}', va='center', fontsize=10, fontweight='bold')
        self._save_figure("final_year_city_rankings.svg")
        plt.close()
# -------------------------------------------------------------------------------------
    def plot_correlation_heatmap(self, overall_results):
        """Plot indicator correlation heatmap"""
        plt.figure(figsize=(8, 6))
        sns.heatmap(overall_results['correlation_matrix'],
                    annot=True, fmt='.4f', cmap='coolwarm',
                    xticklabels=self.indicator_names,
                    yticklabels=self.indicator_names,
                    center=0)
        # plt.title('Indicator Correlation Matrix', fontsize=14, fontweight='bold')
        plt.tight_layout()
        self._save_figure("indicator_correlation_matrix.svg")
        plt.close()

    def _save_figure(self, base_filename):
        """Save figure to the Figure/CRITICS directory with automatic numbering if needed"""
        figures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Output Files", "Figures", "CRITICS")
        os.makedirs(figures_dir, exist_ok=True)
        output_path = os.path.join(figures_dir, base_filename)
        counter = 1
        while os.path.exists(output_path):
            name, ext = os.path.splitext(base_filename)
            output_path = os.path.join(figures_dir, f"{name}_{counter}{ext}")
            counter += 1
        plt.savefig(output_path, format="svg", bbox_inches="tight")
        print(f"\n📊 Figure saved to: {output_path}")

    def export_results(self, overall_results, yearly_results, city_scores, output_file='critic_analysis_results.xlsx'):
        """Export analysis results to Excel"""
        # Ensure the output directory exists
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Output Files')
        os.makedirs(output_dir, exist_ok=True)

        # Check if the file name is already taken, and if so, append a number
        base_name, ext = os.path.splitext(output_file)
        output_path = os.path.join(output_dir, output_file)
        # counter = 1
        # while os.path.exists(output_path):
        #     #output_path = os.path.join(output_dir, f"{base_name}_{counter}{ext}")
        #     output_path = os.path.join(output_dir, f"{base_name}_{counter}{ext}")
        #     counter += 1

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 1. Overall Weights
            overall_df = pd.DataFrame({
                'Indicator': self.indicator_names,
                'Std Dev': overall_results['std_dev'],
                'Information': overall_results['information_amount'],
                'Weight': overall_results['weights'],
                'Weight Percentage': [f'{w * 100:.4f}%' for w in overall_results['weights']]
            })
            overall_df.to_excel(writer, sheet_name='CRITIC Weights', index=False)

            # 2. Yearly Weights
            yearly_weights_data = []
            for year, results in yearly_results.items():
                row = {'Year': year}
                for i, indicator in enumerate(self.indicator_names):
                    row[indicator] = results['weights'][i]
                yearly_weights_data.append(row)

            yearly_df = pd.DataFrame(yearly_weights_data)
            yearly_df.to_excel(writer, sheet_name='Yearly Weights', index=False)

            # 3. City Scores
            city_scores_data = []
            for city, scores in city_scores.items():
                row = {'City': city}
                for year_idx, year in enumerate(self.years):
                    row[year] = scores[year_idx]
                city_scores_data.append(row)

            scores_df = pd.DataFrame(city_scores_data)
            scores_df.to_excel(writer, sheet_name='City Scores', index=False)

            # 4. Correlation Matrix
            corr_df = pd.DataFrame(
                overall_results['correlation_matrix'],
                index=self.indicator_names,
                columns=self.indicator_names
            )
            corr_df.to_excel(writer, sheet_name='Correlation Matrix')

        print(f"\n📁 CRITIC analysis results exported to: {output_path}")


    def export_city_rankings(self, city_scores, output_file='critics_city_rankings_results.xlsx'):
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
        ranking_df['Final Score'] = ranking_df['Final Score'].round(8)
        ranking_df['Average Score'] = ranking_df['Average Score'].round(8)

        # Sort by final rank
        ranking_df = ranking_df.sort_values(by='Final Rank')

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            ranking_df.to_excel(writer, sheet_name='City Rankings', index=False)

        print(f"\n📁 CRITIC city rankings exported to: {output_path}")


# 使用示例
if __name__ == "__main__":
    # Configure parameters - modify as needed
    import os

    # Get the current script directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
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

    INDICATOR_NAMES = ['X1 (Waste)', 'X2 (Water)', 'X3 (Air)', 'X4 (Population)', 'X5 (Energy)', 'X6 (Transport)', 'X7 (Ecology)', 'X8 (Infrastructure)']

    # Create CRITIC analyzer
    critic_analyzer = CRITICAnalyzer(FILE_PATHS, INDICATOR_NAMES)

    # Load data
    data = critic_analyzer.load_and_merge_data()

    if data is not None:
        # Normalize data - 保持pasitive和positive不变
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
        normalized_data = critic_analyzer.normalize_data(data, directions)

        # Perform overall weight analysis
        overall_results = critic_analyzer.analyze_overall_weights(normalized_data)

        # Perform yearly weight analysis
        yearly_results = critic_analyzer.analyze_yearly_weights(normalized_data)

        # Calculate city scores
        city_scores = critic_analyzer.calculate_city_scores(normalized_data, overall_results['weights'])

        # Plot results
        critic_analyzer.plot_critic_analysis(overall_results, yearly_results, city_scores)
        critic_analyzer.plot_correlation_heatmap(overall_results)

        # Export results
        critic_analyzer.export_results(overall_results, yearly_results, city_scores)

        critic_analyzer.export_city_rankings(city_scores)

        # Output final rankings
        print("\n" + "=" * 60)
        print("                  Final City Rankings (CRITIC Method)")
        print("=" * 60)
        final_scores = {city: scores[-1] for city, scores in city_scores.items()}
        ranked_cities = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)

        for rank, (city, score) in enumerate(ranked_cities, 1):
            print(f"🏆 Rank {rank}: {city} - Score: {score:.8f}")

        print(f"\n🎯 CRITIC Analysis Complete! Best City: {ranked_cities[0][0]}")