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

def plot_joint_scatter(df, size_var='Mean', title=None, fig_name=None):
    size_range = (10, df[size_var].max())
    sns.set_theme(style="white", color_codes=True)
    g = sns.JointGrid(data=df, x="Area", y="Max", space=0, ratio=17)
    g.plot_joint(sns.scatterplot, size=df[size_var], sizes=size_range,
                 color="b", alpha=.4, legend=False)
    g.plot_marginals(sns.rugplot, height=1, color="b", alpha=.4)
    g.fig.suptitle(title, y=0.9)
    plt.savefig(fig_name, dpi=400)
    plt.close()