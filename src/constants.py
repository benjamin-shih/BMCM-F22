import matplotlib.pyplot as plt

DATA_PATH = "../data/"
provided_path = "BMCM_2022_data.csv"
FIG_PATH = "../images/"

# scatterplot lambda
sc = lambda df, x, y: plt.scatter(df[x], df[y])

# savefig lambda
sf = lambda name: plt.savefig(FIG_PATH + name)
