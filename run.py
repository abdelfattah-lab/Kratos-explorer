from runs.explore import explore_conv_1d_fu, explore_conv_1d_pw

# results = explore_conv_1d_fu()
# results.to_csv('conv_1d_fu_results.csv')

results = explore_conv_1d_pw()
results.to_csv('conv_1d_pw_results.csv')