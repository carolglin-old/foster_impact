from bokeh.plotting import *
import pdb

# zeros = [0] * len(xs)
# ones = [1] * len(xs)

# p.rect(xs,    # x-coordinates
#        ys,    # y-coordinates
#        ones,  # widths
#        ones,  # heights
#        fill_color="steelblue")

# p.quad(xs[:-1],    # left
#        xs[1:],     # right
#        ys[:-1],    # top
#        ones[:-1],  # bottom
#        fill_color="crimson")

# p.circle(xs, ys,
#          size=ys, # px
#          fill_alpha=0.5,
#          fill_color="steelblue",
#          line_alpha=0.8,
#          line_color="crimson")

# N = 4000

# factors = ["a", "b", "c", "d", "e", "f", "g", "h"]
# x0 = [0, 0, 0, 0, 0, 0, 0, 0]
# x =  [50, 40, 65, 10, 25, 37, 80, 60]

# output_file("categorical.html", title="categorical.py example")

# p1 = figure(title="Dot Plot", tools="resize,save", y_range=factors, x_range=[0,100])

# p1.segment(x0, factors, x, factors, line_width=2, line_color="green", )
# p1.circle(x, factors, size=15, fill_color="orange", line_color="green", line_width=3, )


# show(VBox(p1, p2))  # open a browser


# class DataViz:
# 	def __init__(self, iv, df, y_vals, x_start, x_end, html_name):
# 		self.data = df
# 		self.iv = iv
# 		self.y = y_vals
# 		self.x_start = x_start
# 		self.x_end = x_end
# 		self.output = output_file(html_name, title=html_name)

def dot_plot(self, var_name):
	output_file('dotplot.html', title=iv)
	yv = df[y_vals].astype(str).tolist()
	xs = df[x_start].tolist()
	xe = df[x_end].tolist()
	# y_range = [yv]
	x_range = [df[x_start].min(), df[x_end].max()]
	p1 = figure(
		title=iv+str(len(df)), 
		tools='resize,save,lasso_select,pan,hover', 
		y_range=yv, 
		x_range=x_range
	)
	p1.segment(xs, yv, xe, yv, line_width=6, line_color='green', )
	# p1.circle(xe, yv, size=10, fill_color='orange', line_color='green', line_width=2)
	show(p1)
















