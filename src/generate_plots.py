import matplotlib.pyplot as plt
import seaborn as sns

def plot_scatter_ScaledSize(df, size_var='Mean', title=None, fig_name=None):
    #size_range=(df[size_var].min(), df[size_var].max())
    size_range=(10, df[size_var].max())
    sns.scatterplot(x="Area", y="Max", size=size_var,
            alpha=.5, palette="muted", sizes=size_range,
            data=df).set(title=title)
    plt.savefig(fig_name, dpi=400)
    plt.close()
