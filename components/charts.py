import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

PLOT_BG = "rgba(0,0,0,0)"
PAPER_BG = "rgba(0,0,0,0)"
TEXT_COLOR = "#e2e8f0"

def plot_inventory_by_category(df: pd.DataFrame):
    if df.empty or "Category" not in df.columns:
        return None
    grouped = df.groupby("Category")["Current Qty"].sum().reset_index()
    fig = px.bar(
        grouped,
        x="Category",
        y="Current Qty",
        color="Category",
        title="Vegetable Inventory by Category (kg)",
        color_discrete_sequence=["#10b981", "#3b82f6", "#8b5cf6", "#f59e0b", "#ec4899"],
        labels={"Current Qty": "Stock (kg)"}
    )
    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=TEXT_COLOR),
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
    )
    return fig

def plot_freshness_distribution(df: pd.DataFrame):
    if df.empty or "Freshness Condition" not in df.columns:
        return None
    grouped = df.groupby("Freshness Condition")["Current Qty"].sum().reset_index()
    color_map = {"Fresh": "#10b981", "Ripe": "#f59e0b", "Spoiled": "#ef4444"}
    fig = px.pie(
        grouped,
        names="Freshness Condition",
        values="Current Qty",
        title="Stock by Freshness State",
        hole=0.55,
        color="Freshness Condition",
        color_discrete_map=color_map
    )
    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=TEXT_COLOR),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def plot_usage_vs_waste(metrics: dict):
    labels = ["Used in Cooking", "Current Stock", "Food Waste"]
    values = [metrics.get("total_used_qty", 0), metrics.get("current_stock_qty", 0), metrics.get("total_wasted_qty", 0)]
    colors = ["#10b981", "#3b82f6", "#ef4444"]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5, marker=dict(colors=colors))])
    fig.update_layout(
        title="Total Food Allocation Breakdown",
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=TEXT_COLOR),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def plot_waste_by_reason(waste_df: pd.DataFrame):
    if waste_df.empty or "Reason" not in waste_df.columns:
        return None
    grouped = waste_df.groupby("Reason")["Quantity Wasted"].sum().reset_index()
    fig = px.bar(
        grouped,
        x="Reason",
        y="Quantity Wasted",
        title="Waste by Cause / Reason",
        color="Reason",
        color_discrete_sequence=["#ef4444", "#f97316", "#eab308", "#64748b"],
        labels={"Quantity Wasted": "Wasted Qty (kg)"}
    )
    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=TEXT_COLOR),
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)")
    )
    return fig
