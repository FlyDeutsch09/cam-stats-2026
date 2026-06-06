import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import warnings
import os

warnings.filterwarnings('ignore')


class EntropyWeightMethod:
    def __init__(self, file_paths, indicator_names, indicator_directions=None):
        self.file_paths = file_paths
        self.indicator_names = indicator_names
        if indicator_directions is None:
            # Default all to positive if not provided
            self.indicator_directions = {indicator: 'positive' for indicator in indicator_names}
        else:
            self.indicator_directions = indicator_directions

    def load_data(self):
        """Load data from multiple Excel files"""
        print("Loading data...")
        all_data = {}

        # Read the first file to get city names and years
        first_df = pd.read_excel(self.file_paths[0], index_col=0)
        self.cities = first_df.columns.tolist()  # Column names are city names
        self.years = first_df.index.tolist()  # Row indices are years

        print(f"Found {len(self.cities)} cities: {self.cities}")
        # DEBUG: Confirm data orientation (Rows=Years, Columns=Cities)
        print(f"DEBUG: First 5 Cities (Columns): {self.cities[:5]}")
        print(f"DEBUG: First 5 Years (Rows/Index): {self.years[:5]}")
        print(f"Found {len(self.years)} years: {self.years}")

        for i, file_path in enumerate(self.file_paths):
            print(f"Loading file: {file_path} - Indicator: {self.indicator_names[i]}")

            try:
                # Read Excel file
                df = pd.read_excel(file_path, index_col=0)

                # Validate data format
                if not all(df.columns == self.cities):
                    print(f"Adjusting city order for {self.indicator_names[i]}")
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

    def normalize_data(self, data):
        """Normalize data"""
        directions = self.indicator_directions
        normalized_data = {}

        for city, city_data in data.items():
            normalized_city_data = {}
            for indicator, values in city_data.items():
                values = np.array(values, dtype=float)

                if directions[indicator] == 'positive':
                    # 正向指标标准化
                    min_val = np.min(values)
                    max_val = np.max(values)
                    if max_val == min_val:
                        normalized_values = np.ones_like(values)
                    else:
                        normalized_values = (values - min_val) / (max_val - min_val)
                else:
                    # 负向指标标准化
                    min_val = np.min(values)
                    max_val = np.max(values)
                    if max_val == min_val:
                        normalized_values = np.ones_like(values)
                    else:
                        normalized_values = (max_val - values) / (max_val - min_val)

                # 避免0值（对数计算需要）
                normalized_values = np.where(normalized_values == 0, 0.0001, normalized_values)
                normalized_city_data[indicator] = normalized_values

            normalized_data[city] = normalized_city_data

        return normalized_data

    def calculate_entropy_weights(self, data, method='comprehensive'):
        """Calculate entropy weights"""
        if method == 'comprehensive':
            return self._calculate_comprehensive_weights(data)
        else:
            return self._calculate_yearly_weights(data)

    def _calculate_comprehensive_weights(self, data):
        """Calculate comprehensive entropy weights"""
        print("\n" + "=" * 60)
        print("                  Comprehensive Entropy Weight Calculation")
        print("=" * 60)

        n_cities = len(self.cities)
        n_indicators = len(self.indicator_names)
        n_years = len(self.years)

        # 构建数据矩阵: (指标数, 城市数×年份数)
        data_matrix = np.zeros((n_indicators, n_cities * n_years))

        for i, indicator in enumerate(self.indicator_names):
            all_values = []
            for city in self.cities:
                all_values.extend(data[city][indicator])
            data_matrix[i, :] = all_values

        print(f"数据矩阵维度: {data_matrix.shape}")

        # 计算比重
        p_matrix = data_matrix / np.sum(data_matrix, axis=1, keepdims=True)

        # 计算熵值
        k = 1 / np.log(n_cities * n_years)  # 熵系数
        e_values = -k * np.sum(p_matrix * np.log(p_matrix), axis=1)

        # 计算差异系数
        d_values = 1 - e_values

        # 计算权重
        weights = d_values / np.sum(d_values)

        # 输出详细计算过程
        print("\n📊 Entropy Weight Calculation Process:")
        for i, indicator in enumerate(self.indicator_names):
            print(f"  {indicator}:")
            print(f"    Entropy e = {e_values[i]:.6f}")
            print(f"    Divergence d = {d_values[i]:.6f}")
            print(f"    Weight w = {weights[i]:.6f} ({weights[i] * 100:.2f}%)")

        results = {
            'weights': weights,
            'entropy_values': e_values,
            'divergence_values': d_values,
            'method': 'comprehensive'
        }

        return results

    def _calculate_yearly_weights(self, data):
        """Calculate yearly entropy weights"""
        print("\n" + "=" * 60)
        print("                  Yearly Entropy Weight Calculation")
        print("=" * 60)

        yearly_results = {}

        for year_idx, year in enumerate(self.years):
            print(f"\n📅 年份 {year}:")

            # 构建该年份的数据矩阵: (指标数, 城市数)
            data_matrix = np.zeros((len(self.indicator_names), len(self.cities)))

            for i, indicator in enumerate(self.indicator_names):
                year_values = []
                for city in self.cities:
                    year_values.append(data[city][indicator][year_idx])
                data_matrix[i, :] = year_values

            # 计算比重
            p_matrix = data_matrix / np.sum(data_matrix, axis=1, keepdims=True)

            # 计算熵值
            k = 1 / np.log(len(self.cities))  # 熵系数
            e_values = -k * np.sum(p_matrix * np.log(p_matrix), axis=1)

            # 计算差异系数
            d_values = 1 - e_values

            # 计算权重
            weights = d_values / np.sum(d_values)

            yearly_results[year] = {
                'weights': weights,
                'entropy_values': e_values,
                'divergence_values': d_values
            }

            for i, indicator in enumerate(self.indicator_names):
                print(f"  {indicator}: Weight = {weights[i]:.4f}")

        return yearly_results

    def calculate_city_scores(self, data, weights):
        """Calculate overall scores for each city"""
        city_scores = {}

        print("\n" + "=" * 60)
        print("                  City Overall Score Calculation")
        print("=" * 60)

        for city in self.cities:
            scores_by_year = []
            for year_idx, year in enumerate(self.years):
                year_score = 0
                for i, indicator in enumerate(self.indicator_names):
                    year_score += data[city][indicator][year_idx] * weights[i]
                scores_by_year.append(year_score)
            city_scores[city] = scores_by_year

            print(f"\n🏙️ {city}:")
            print(f"  Score Trend: {[f'{s:.4f}' for s in scores_by_year]}")
            print(f"  Average Score: {np.mean(scores_by_year):.4f}")
            print(f"  Score Growth: {scores_by_year[-1] - scores_by_year[0]:.4f}")

        return city_scores


class AHP_Entropy_Comparison:
    def __init__(self, file_paths, indicator_names, indicator_directions=None):
        self.file_paths = file_paths
        self.indicator_names = indicator_names
        # 修复拼写错误
        if indicator_directions is not None:
            for key in list(indicator_directions.keys()):
                if indicator_directions[key] == 'pasitive':
                    indicator_directions[key] = 'positive'
        self.indicator_directions = indicator_directions
        self.entropy_analyzer = EntropyWeightMethod(file_paths, indicator_names, indicator_directions)

    def run_comparison_analysis(self):
        """运行AHP与熵权法的比较分析"""
        # 加载数据
        data = self.entropy_analyzer.load_data()

        if data is None:
            return

        # 数据标准化
        normalized_data = self.entropy_analyzer.normalize_data(data)

        # 熵权法分析
        print("\n" + "🔍" * 30)
        print("          熵权法分析开始")
        print("🔍" * 30)

        entropy_results = self.entropy_analyzer.calculate_entropy_weights(normalized_data, 'comprehensive')
        yearly_entropy_results = self.entropy_analyzer.calculate_entropy_weights(normalized_data, 'yearly')

        # AHP分析
        ahp_results = self._run_ahp_analysis(normalized_data)

        # 计算城市得分
        entropy_scores = self.entropy_analyzer.calculate_city_scores(normalized_data, entropy_results['weights'])
        ahp_scores = self.entropy_analyzer.calculate_city_scores(normalized_data, ahp_results['weights'])

        # 比较分析
        self._compare_methods(entropy_results, ahp_results, entropy_scores, ahp_scores)

        # 可视化结果
        self._plot_comparison_results(entropy_results, ahp_results, entropy_scores, ahp_scores, yearly_entropy_results)

        return entropy_results, ahp_results, entropy_scores, ahp_scores

    def _run_ahp_analysis(self, data):
        """运行AHP分析（简化版）"""
        print("\n" + "🔍" * 30)
        print("          AHP分析开始")
        print("🔍" * 30)

        # 基于变异系数构建比较矩阵
        indicator_variability = {}

        for indicator in self.indicator_names:
            all_values = []
            for city_data in data.values():
                all_values.extend(city_data[indicator])
            mean_val = np.mean(all_values)
            std_val = np.std(all_values)
            cv = std_val / mean_val if mean_val != 0 else 0
            indicator_variability[indicator] = cv

        print("各指标变异系数:")
        for indicator, cv in indicator_variability.items():
            print(f"  {indicator}: {cv:.4f}")

        # 构建比较矩阵
        comparisons = []
        for i, ind1 in enumerate(self.indicator_names):
            row = []
            for j, ind2 in enumerate(self.indicator_names):
                if i == j:
                    row.append(1)
                else:
                    cv1 = indicator_variability[ind1]
                    cv2 = indicator_variability[ind2]
                    ratio = cv1 / cv2 if cv2 != 0 else 1

                    # 映射到1-9标度
                    if ratio >= 1.8:
                        score = 9
                    elif ratio >= 1.6:
                        score = 8
                    elif ratio >= 1.4:
                        score = 7
                    elif ratio >= 1.2:
                        score = 6
                    elif ratio >= 1.1:
                        score = 5
                    elif ratio >= 1.0:
                        score = 4
                    elif ratio >= 0.9:
                        score = 3
                    elif ratio >= 0.7:
                        score = 2
                    else:
                        score = 1

                    if ratio < 1: 
                        score = 1 / score if score != 1 else 1
                    row.append(score)
            comparisons.append(row)

        # 计算AHP权重
        matrix = np.array(comparisons)
        eigenvalues, eigenvectors = np.linalg.eig(matrix)
        max_eigenvalue_index = np.argmax(eigenvalues.real)
        weights = np.abs(eigenvectors[:, max_eigenvalue_index].real)
        weights = weights / np.sum(weights)

        print("\n📊 AHP指标权重:")
        for i, indicator in enumerate(self.indicator_names):
            print(f"  {indicator}: {weights[i]:.4f} ({weights[i] * 100:.2f}%)")

        return {'weights': weights, 'comparison_matrix': matrix}

    def _compare_methods(self, entropy_results, ahp_results, entropy_scores, ahp_scores):
        """Compare the differences between two methods"""
        print("\n" + "=" * 60)
        print("                 Method Comparison Analysis")
        print("=" * 60)

        # Weight comparison
        print("\n📈 Weight Comparison:")
        print("Indicator     Entropy Weight    AHP Weight     Difference")
        print("-" * 50)

        for i, indicator in enumerate(self.indicator_names):
            entropy_w = entropy_results['weights'][i]
            ahp_w = ahp_results['weights'][i]
            diff = entropy_w - ahp_w
            print(f"{indicator:10} {entropy_w:10.4f} {ahp_w:10.4f} {diff:10.4f}")

        # City ranking comparison
        print("\n🏆 City Ranking Comparison:")

        # Entropy method ranking
        final_entropy_scores = {city: scores[-1] for city, scores in entropy_scores.items()}
        entropy_ranking = sorted(final_entropy_scores.items(), key=lambda x: x[1], reverse=True)

        # AHP ranking
        final_ahp_scores = {city: scores[-1] for city, scores in ahp_scores.items()}
        ahp_ranking = sorted(final_ahp_scores.items(), key=lambda x: x[1], reverse=True)

        print("City       Entropy Rank  AHP Rank  Rank Difference")
        print("-" * 40)

        rank_differences = []
        for city in self.entropy_analyzer.cities:
            entropy_rank = [i for i, (c, _) in enumerate(entropy_ranking, 1) if c == city][0]
            ahp_rank = [i for i, (c, _) in enumerate(ahp_ranking, 1) if c == city][0]
            rank_diff = entropy_rank - ahp_rank
            rank_differences.append(abs(rank_diff))

            print(f"{city:8} {entropy_rank:12} {ahp_rank:9} {rank_diff:15}")

        # Consistency analysis
        correlation = np.corrcoef(
            [score for _, score in entropy_ranking],
            [score for _, score in ahp_ranking]
        )[0, 1]

        print(f"\n📊 Method Consistency Analysis:")
        print(f"Ranking Correlation Coefficient: {correlation:.4f}")
        print(f"Average Rank Difference: {np.mean(rank_differences):.2f}")

        if correlation > 0.8:
            print("✅ The results of the two methods are highly consistent")
        elif correlation > 0.6:
            print("⚠️ The results of the two methods are moderately consistent")
        else:
            print("❌ The results of the two methods differ significantly")

    def _plot_comparison_results(self, entropy_results, ahp_results, entropy_scores, ahp_scores,
                                 yearly_entropy_results):
        """Plot comparison results"""
        plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

        # 1. Weight Comparison Bar Chart
        plt.figure(figsize=(8, 6))
        x = np.arange(len(self.indicator_names))
        width = 0.35
        plt.bar(x - width / 2, entropy_results['weights'], width, label='Entropy Weight Method', alpha=0.7)
        plt.bar(x + width / 2, ahp_results['weights'], width, label='AHP', alpha=0.7)
        plt.title('Indicator Weight Comparison', fontweight='bold')
        plt.xlabel('Indicators')
        plt.ylabel('Weight')
        plt.xticks(x, self.indicator_names, fontsize=5)
        plt.legend()
        plt.grid(True, alpha=0.3)
        self._save_figure("indicator_weight_comparison.svg")
        plt.close()

        # 2. Entropy Values
        plt.figure(figsize=(8, 6))
        plt.bar(self.indicator_names, entropy_results['entropy_values'], color='lightcoral', alpha=0.7)
        plt.title('Entropy Values', fontweight='bold')
        plt.ylabel('Entropy')
        plt.xticks(fontsize=5)
        plt.grid(True, alpha=0.3)
        self._save_figure("entropy_values.svg")
        plt.close()

        # 3. Divergence Coefficients
        plt.figure(figsize=(8, 6))
        plt.bar(self.indicator_names, entropy_results['divergence_values'], color='lightgreen', alpha=0.7)
        plt.title('Divergence Coefficients', fontweight='bold')
        plt.ylabel('Divergence')
        plt.xticks(fontsize=5)
        plt.grid(True, alpha=0.3)
        self._save_figure("divergence_coefficients.svg")
        plt.close()

        # 4. City Score Comparison (Final Year)
        plt.figure(figsize=(8, 6))
        final_entropy = {city: scores[-1] for city, scores in entropy_scores.items()}
        final_ahp = {city: scores[-1] for city, scores in ahp_scores.items()}
        cities = list(final_entropy.keys())
        entropy_values = [final_entropy[city] for city in cities]
        ahp_values = [final_ahp[city] for city in cities]
        x = np.arange(len(cities))
        plt.bar(x - width / 2, entropy_values, width, label='Entropy Weight Method', alpha=0.7)
        plt.bar(x + width / 2, ahp_values, width, label='AHP', alpha=0.7)
        plt.title('City Score Comparison (Final Year)', fontweight='bold')
        plt.xlabel('Cities')
        plt.ylabel('Score')
        plt.xticks(x, cities, rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3)
        self._save_figure("city_score_comparison_final_year.svg")
        plt.close()

        # 5. Yearly Weight Changes (Entropy Weight Method)
        plt.figure(figsize=(8, 6))
        years = list(yearly_entropy_results.keys())
        weights_data = {indicator: [] for indicator in self.indicator_names}
        for year in years:
            weights = yearly_entropy_results[year]['weights']
            for i, indicator in enumerate(self.indicator_names):
                weights_data[indicator].append(weights[i])
        for indicator in self.indicator_names:
            plt.plot(years, weights_data[indicator], marker='o', label=indicator, linewidth=2)
        plt.title('Yearly Weight Changes (Entropy Weight Method)', fontweight='bold')
        plt.xlabel('Year')
        plt.ylabel('Weight')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tick_params(axis='x', rotation=45)
        self._save_figure("yearly_weight_changes.svg")
        plt.close()

        # 6. Method Difference Heatmap
        plt.figure(figsize=(8, 6))
        correlation_matrix = np.zeros((len(self.entropy_analyzer.cities), 2))
        for i, city in enumerate(self.entropy_analyzer.cities):
            correlation_matrix[i, 0] = final_entropy[city]
            correlation_matrix[i, 1] = final_ahp[city]
        sns.heatmap(correlation_matrix, cmap='YlOrRd', annot=True, fmt='.3f', xticklabels=['Entropy', 'AHP'],
                    yticklabels=self.entropy_analyzer.cities)
        plt.title('City Score Method Differences', fontweight='bold')
        plt.xlabel('Method')
        plt.ylabel('City')
        self._save_figure("city_score_method_differences.svg")
        plt.close()

    def _save_figure(self, base_filename):
        """Save figure to the Figure/Entropy directory with automatic numbering if needed"""
        figures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Output Files", "Figures", "Entropy")
        os.makedirs(figures_dir, exist_ok=True)
        output_path = os.path.join(figures_dir, base_filename)
        counter = 1
        while os.path.exists(output_path):
            name, ext = os.path.splitext(base_filename)
            output_path = os.path.join(figures_dir, f"{name}_{counter}{ext}")
            counter += 1
        plt.savefig(output_path, format="svg", bbox_inches="tight")
        print(f"\n📊 Figure saved to: {output_path}")

    def export_comparison_results(self, entropy_results, ahp_results, entropy_scores, ahp_scores,
                                  output_file='entropy_results.xlsx'):
        """Export comparison results to Excel"""
        # Ensure the output directory exists
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Output Files')
        os.makedirs(output_dir, exist_ok=True)

        # Check if the file name is already taken, and if so, append a number
        base_name, ext = os.path.splitext(output_file)
        output_path = os.path.join(output_dir, output_file)
        # counter = 1
        # while os.path.exists(output_path):
        #     output_path = os.path.join(output_dir, f"{base_name}_{counter}{ext}")
        #     counter += 1

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 1. Weight Comparison
            weights_df = pd.DataFrame({
                'Indicator': self.indicator_names,
                'Entropy Weight': entropy_results['weights'],
                'AHP Weight': ahp_results['weights'],
                'Weight Difference': entropy_results['weights'] - ahp_results['weights']
            })
            weights_df.to_excel(writer, sheet_name='Weight Comparison', index=False)

            # 2. Entropy Method Details
            entropy_detail_df = pd.DataFrame({
                'Indicator': self.indicator_names,
                'Entropy': entropy_results['entropy_values'],
                'Divergence': entropy_results['divergence_values'],
                'Weight': entropy_results['weights']
            })
            entropy_detail_df.to_excel(writer, sheet_name='Entropy Method Details', index=False)

            # 3. City Score Comparison
            scores_comparison = []
            for city in self.entropy_analyzer.cities:
                row = {'City': city}
                row['Entropy Final Score'] = entropy_scores[city][-1]
                row['AHP Final Score'] = ahp_scores[city][-1]
                row['Score Difference'] = entropy_scores[city][-1] - ahp_scores[city][-1]
                scores_comparison.append(row)

            scores_df = pd.DataFrame(scores_comparison)
            scores_df.to_excel(writer, sheet_name='City Score Comparison', index=False)

            # 4. Time Series Scores
            yearly_scores_data = []
            for year_idx, year in enumerate(self.entropy_analyzer.years):
                for city in self.entropy_analyzer.cities:
                    row = {'Year': year, 'City': city}
                    row['Entropy Score'] = entropy_scores[city][year_idx]
                    row['AHP Score'] = ahp_scores[city][year_idx]
                    yearly_scores_data.append(row)

            yearly_scores_df = pd.DataFrame(yearly_scores_data)
            yearly_scores_df.to_excel(writer, sheet_name='Time Series Scores', index=False)

        print(f"\n📊 Comparison analysis results exported to: {output_path}")

    def export_entropy_city_rankings(self, entropy_scores, output_file='entropy_city_rankings_results.xlsx'):
        """Export final year city rankings based on Entropy method to Excel"""
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Output Files')
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, output_file)
        
        # Get final year scores and calculate average scores
        final_scores = {}
        average_scores = {}
        
        for city, scores in entropy_scores.items():
            final_scores[city] = scores[-1]
            average_scores[city] = np.mean(scores)
        
        # Create DataFrame for final scores and average scores
        ranking_data = []
        for city in self.entropy_analyzer.cities:
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

        print(f"\n📁 Entropy city rankings exported to: {output_path}")

    def export_ahp_city_rankings(self, ahp_scores, output_file='ahp_city_rankings_results.xlsx'):
        """Export final year city rankings based on AHP method to Excel"""
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Output Files')
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, output_file)
        
        # Get final year scores and calculate average scores
        final_scores = {}
        average_scores = {}
        
        for city, scores in ahp_scores.items():
            final_scores[city] = scores[-1]
            average_scores[city] = np.mean(scores)
        
        # Create DataFrame for final scores and average scores
        ranking_data = []
        for city in self.entropy_analyzer.cities:
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


# 使用示例
if __name__ == "__main__":
    # Configure parameters
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

    INDICATOR_NAMES = ['X1 (Waste)', 'X2 (Water)', 'X3 (Air)', 'X4 (Population)', 'X5 (Energy)', 'X6 (Transport)', 'X7 (Ecology)', 'X8 (Infrastructure)']  # 替换为您的实际指标名称
    """
    Waste --> Solid_Waste.xlsx
    Water --> Water_Use.xlsx
    Air --> Air_Quality.xlsx
    Population --> Population_Density.xlsx
    Energy --> Electricity_Generated.xlsx
    Transport --> Transport.xlsx
    Ecology --> Greening_Impact_Index.xlsx
    Infrastructure --> Have_Stadium.xlsx
    """

    # Define indicator directions (positive: larger is better, negative: smaller is better)
    # 修复拼写错误
    INDICATOR_DIRECTIONS = {
        'X1 (Waste)': 'positive',
        'X2 (Water)': 'positive',
        'X3 (Air)': 'positive',
        'X4 (Population)': 'positive',
        'X5 (Energy)': 'positive',
        'X6 (Transport)': 'positive',
        'X7 (Ecology)': 'positive',
        'X8 (Infrastructure)': 'pasitive'
    }

    # Create comparison analyzer
    comparator = AHP_Entropy_Comparison(FILE_PATHS, INDICATOR_NAMES, INDICATOR_DIRECTIONS)

    # Run comparison analysis
    results = comparator.run_comparison_analysis()

    if results:
        entropy_results, ahp_results, entropy_scores, ahp_scores = results

        # Export results
        comparator.export_comparison_results(
            entropy_results, ahp_results, entropy_scores, ahp_scores
        )
        
        # Export Entropy rankings
        comparator.export_entropy_city_rankings(entropy_scores)
        
        # Export AHP rankings
        comparator.export_ahp_city_rankings(ahp_scores)

        print("\n🎉 Entropy Weight Method and AHP Comparison Analysis Complete!")