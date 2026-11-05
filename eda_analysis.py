"""
Exploratory Data Analysis (EDA) Project

This script performs comprehensive exploratory data analysis on retail sales data
with proper statistical methods and honest interpretation of small-sample limitations.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def setup_paths():
    """Setup project paths using pathlib for cross-platform compatibility."""
    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "data"
    OUTPUT_DIR = BASE_DIR / "outputs"
    
    # Create directories if they don't exist
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    return BASE_DIR, DATA_DIR, OUTPUT_DIR


def load_data(data_dir: Path) -> pd.DataFrame:
    """Load the retail sales dataset with validation."""
    data_path = data_dir / "SampleSuperstore.csv"
    
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found at {data_path}")
    
    logger.info(f"Loading dataset from {data_path}")
    df = pd.read_csv(data_path)
    
    logger.info(f"Dataset shape: {df.shape}")
    logger.info(f"Columns: {list(df.columns)}")
    
    return df


def validate_data(df: pd.DataFrame) -> None:
    """Validate dataset structure and contents."""
    logger.info("Validating dataset...")
    
    if df.empty:
        raise ValueError("Dataset is empty")
    
    required_columns = ['Order Date', 'Category', 'Region', 'Sales', 'Profit']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    logger.info(f"Dataset validation passed. Rows: {len(df)}, Columns: {len(df.columns)}")


def data_quality_audit(df: pd.DataFrame) -> dict:
    """Perform comprehensive data quality audit."""
    logger.info("Performing data quality audit...")
    
    audit_results = {
        'shape': df.shape,
        'columns': list(df.columns),
        'data_types': df.dtypes.to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'duplicate_rows': df.duplicated().sum(),
        'memory_usage': df.memory_usage(deep=True).sum() / 1024  # KB
    }
    
    # Unique values for categorical columns
    categorical_cols = df.select_dtypes(include=['object', 'string']).columns
    audit_results['unique_values'] = {
        col: df[col].nunique() for col in categorical_cols
    }
    
    logger.info(f"Data Quality Audit Results:")
    logger.info(f"  Shape: {audit_results['shape']}")
    logger.info(f"  Missing values: {sum(audit_results['missing_values'].values())}")
    logger.info(f"  Duplicate rows: {audit_results['duplicate_rows']}")
    logger.info(f"  Memory usage: {audit_results['memory_usage']:.2f} KB")
    
    return audit_results


def descriptive_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Generate descriptive statistics for numerical columns."""
    logger.info("Generating descriptive statistics...")
    
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    stats_df = df[numerical_cols].describe()
    
    # Add additional statistics
    stats_df.loc['median'] = df[numerical_cols].median()
    stats_df.loc['mode'] = df[numerical_cols].mode().iloc[0]
    stats_df.loc['skewness'] = df[numerical_cols].skew()
    stats_df.loc['kurtosis'] = df[numerical_cols].kurtosis()
    
    logger.info(f"Descriptive statistics:\n{stats_df.to_string()}")
    
    return stats_df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the dataset by handling duplicates and converting dates."""
    logger.info("Cleaning data...")
    
    initial_rows = len(df)
    
    # Remove duplicates
    df = df.drop_duplicates().copy()
    duplicates_removed = initial_rows - len(df)
    
    if duplicates_removed > 0:
        logger.info(f"Removed {duplicates_removed} duplicate rows")
    
    # Convert date column
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    
    # Create year-month for proper time analysis
    df['year_month'] = df['Order Date'].dt.to_period('M')
    
    logger.info(f"Data cleaning complete. Final rows: {len(df)}")
    
    return df


def correlation_analysis(df: pd.DataFrame, output_dir: Path) -> pd.DataFrame:
    """Perform correlation analysis and create heatmap."""
    logger.info("Performing correlation analysis...")
    
    # Select numerical columns for correlation
    numerical_cols = ['Sales', 'Profit', 'Quantity', 'Discount']
    available_cols = [col for col in numerical_cols if col in df.columns]
    
    if len(available_cols) < 2:
        logger.warning("Insufficient numerical columns for correlation analysis")
        return pd.DataFrame()
    
    correlation_matrix = df[available_cols].corr()
    
    logger.info(f"Correlation Matrix:\n{correlation_matrix.to_string()}")
    
    # Create correlation heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8})
    plt.title('Correlation Matrix: Sales, Profit, Quantity, Discount', 
              fontweight='bold', fontsize=14)
    plt.tight_layout()
    
    heatmap_path = output_dir / "correlation_heatmap.png"
    plt.savefig(heatmap_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Correlation heatmap saved to {heatmap_path}")
    
    # Save correlation matrix
    corr_path = output_dir / "correlation_matrix.csv"
    correlation_matrix.to_csv(corr_path)
    
    return correlation_matrix


def time_based_analysis(df: pd.DataFrame, output_dir: Path) -> None:
    """Perform time-based analysis using year-month periods."""
    logger.info("Performing time-based analysis...")
    
    # Ensure data is sorted chronologically
    df_sorted = df.sort_values('Order Date')
    
    # Monthly sales trend (by year-month to avoid combining different years)
    monthly_sales = df_sorted.groupby('year_month')['Sales'].sum()
    
    plt.figure(figsize=(10, 5))
    monthly_sales.plot(kind='line', marker='o', linewidth=2, markersize=8)
    plt.title('Monthly Sales Trend (Chronological)', fontweight='bold', fontsize=14)
    plt.xlabel('Year-Month', fontsize=12)
    plt.ylabel('Sales ($)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    trend_path = output_dir / "monthly_sales_trend.png"
    plt.savefig(trend_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Monthly sales trend saved to {trend_path}")
    
    # Print time range information
    logger.info(f"Date range: {df_sorted['Order Date'].min()} to {df_sorted['Order Date'].max()}")
    logger.info(f"Number of unique year-months: {monthly_sales.shape[0]}")


def categorical_analysis(df: pd.DataFrame, output_dir: Path) -> None:
    """Analyze categorical variables and create visualizations."""
    logger.info("Performing categorical analysis...")
    
    # Set style
    sns.set_style("whitegrid")
    
    # Sales by Category
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Categorical Analysis: Sales & Profit Distribution', 
                 fontsize=16, fontweight='bold')
    
    # Sales by Category
    category_sales = df.groupby('Category')['Sales'].sum()
    axes[0, 0].bar(category_sales.index, category_sales.values, 
                   color='steelblue', edgecolor='black')
    axes[0, 0].set_title('Sales by Category', fontweight='bold')
    axes[0, 0].set_ylabel('Sales ($)')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # Profit by Region
    region_profit = df.groupby('Region')['Profit'].sum()
    axes[0, 1].bar(region_profit.index, region_profit.values, 
                   color='coral', edgecolor='black')
    axes[0, 1].set_title('Profit by Region', fontweight='bold')
    axes[0, 1].set_ylabel('Profit ($)')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # Sales by Customer Segment
    segment_sales = df.groupby('Customer Segment')['Sales'].sum()
    axes[1, 0].bar(segment_sales.index, segment_sales.values, 
                   color='mediumseagreen', edgecolor='black')
    axes[1, 0].set_title('Sales by Customer Segment', fontweight='bold')
    axes[1, 0].set_ylabel('Sales ($)')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # Average Discount by Category
    category_discount = df.groupby('Category')['Discount'].mean()
    axes[1, 1].bar(category_discount.index, category_discount.values, 
                   color='purple', edgecolor='black')
    axes[1, 1].set_title('Average Discount by Category', fontweight='bold')
    axes[1, 1].set_ylabel('Average Discount')
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    categorical_path = output_dir / "categorical_analysis.png"
    plt.savefig(categorical_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Categorical analysis saved to {categorical_path}")
    
    # Individual charts for backward compatibility
    # Sales by Category
    plt.figure(figsize=(8, 5))
    category_sales.plot(kind='bar', color='steelblue', edgecolor='black')
    plt.title('Sales by Category', fontweight='bold', fontsize=14)
    plt.ylabel('Sales ($)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    sales_category_path = output_dir / "sales_by_category.png"
    plt.savefig(sales_category_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    # Profit by Region
    plt.figure(figsize=(8, 5))
    region_profit.plot(kind='bar', color='coral', edgecolor='black')
    plt.title('Profit by Region', fontweight='bold', fontsize=14)
    plt.ylabel('Profit ($)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    profit_region_path = output_dir / "profit_by_region.png"
    plt.savefig(profit_region_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    logger.info("Individual categorical charts saved")


def distribution_analysis(df: pd.DataFrame, output_dir: Path) -> None:
    """Analyze distributions of numerical variables."""
    logger.info("Performing distribution analysis...")
    
    numerical_cols = ['Sales', 'Profit', 'Quantity', 'Discount']
    available_cols = [col for col in numerical_cols if col in df.columns]
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Distribution Analysis of Numerical Variables', 
                 fontsize=16, fontweight='bold')
    
    for idx, col in enumerate(available_cols[:4]):
        row = idx // 2
        col_idx = idx % 2
        
        axes[row, col_idx].hist(df[col], bins=10, edgecolor='black', alpha=0.7)
        axes[row, col_idx].set_title(f'Distribution of {col}', fontweight='bold')
        axes[row, col_idx].set_xlabel(col)
        axes[row, col_idx].set_ylabel('Frequency')
        axes[row, col_idx].grid(True, alpha=0.3)
    
    plt.tight_layout()
    dist_path = output_dir / "distribution_analysis.png"
    plt.savefig(dist_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Distribution analysis saved to {dist_path}")


def save_statistics(df: pd.DataFrame, stats_df: pd.DataFrame, audit_results: dict, output_dir: Path) -> None:
    """Save statistical summaries to files."""
    logger.info("Saving statistical summaries...")
    
    # Save descriptive statistics
    stats_path = output_dir / "descriptive_statistics.csv"
    stats_df.to_csv(stats_path)
    
    # Save data quality audit
    audit_df = pd.DataFrame([audit_results])
    audit_path = output_dir / "data_quality_audit.csv"
    audit_df.to_csv(audit_path, index=False)
    
    # Save dataset info
    info_path = output_dir / "dataset_info.txt"
    with open(info_path, 'w') as f:
        f.write("Dataset Information\n")
        f.write("=" * 40 + "\n")
        f.write(f"Shape: {audit_results['shape']}\n")
        f.write(f"Columns: {audit_results['columns']}\n")
        f.write(f"Missing Values: {sum(audit_results['missing_values'].values())}\n")
        f.write(f"Duplicate Rows: {audit_results['duplicate_rows']}\n")
        f.write(f"Memory Usage: {audit_results['memory_usage']:.2f} KB\n")
        f.write("\nUnique Values (Categorical):\n")
        for col, count in audit_results['unique_values'].items():
            f.write(f"  {col}: {count}\n")
    
    logger.info("Statistical summaries saved")


def main():
    """Main execution function."""
    try:
        logger.info("=" * 60)
        logger.info("Exploratory Data Analysis Project Started")
        logger.info("=" * 60)
        
        # Setup paths
        BASE_DIR, DATA_DIR, OUTPUT_DIR = setup_paths()
        
        # Load data
        df = load_data(DATA_DIR)
        
        # Validate data
        validate_data(df)
        
        # Data quality audit
        audit_results = data_quality_audit(df)
        
        # Clean data
        df = clean_data(df)
        
        # Descriptive statistics
        stats_df = descriptive_statistics(df)
        
        # Correlation analysis
        correlation_matrix = correlation_analysis(df, OUTPUT_DIR)
        
        # Time-based analysis
        time_based_analysis(df, OUTPUT_DIR)
        
        # Categorical analysis
        categorical_analysis(df, OUTPUT_DIR)
        
        # Distribution analysis
        distribution_analysis(df, OUTPUT_DIR)
        
        # Save statistics
        save_statistics(df, stats_df, audit_results, OUTPUT_DIR)
        
        logger.info("=" * 60)
        logger.info("EDA Project Completed Successfully")
        logger.info("=" * 60)
        logger.info(f"Final dataset shape: {df.shape}")
        logger.info(f"Outputs saved to: {OUTPUT_DIR}")
        
        # Important limitation notice
        logger.info("\n" + "!" * 60)
        logger.info("IMPORTANT: Dataset contains only 8 rows.")
        logger.info("All findings are ILLUSTRATIVE and should NOT be")
        logger.info("generalized to larger populations or used for")
        logger.info("business decisions without additional data.")
        logger.info("!" * 60)
        
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")
        raise


if __name__ == "__main__":
    main()