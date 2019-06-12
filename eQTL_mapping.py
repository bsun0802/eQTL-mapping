import argparse
import warnings

import pandas as pd
import numpy as np

import statsmodels.api as sm
import scipy.stats as ss


def parse_arguments():
    parser = argparse.ArgumentParser(description="eQTL mapping")
    parser.add_argument(
        'expr', help='Expression matrix (csv format), rows are genes columns are samples')
    parser.add_argument(
        'covar', help='Covariates, assume the same order with samples in expressions')
    ''' Variants files are usually generated by scan variants calling VCF file
    for gene nearby variants and take the genotype out'''
    parser.add_argument('variants',
                        help='Variants file (csv format), assume samples are in the same order as in expressions')
    parser.add_argument('output', help='Output File')

    parser.add_argument('--int', help='Turn on Inverse-Normal-Transformation', action='store_true')
    parser.add_argument('-m', '--model', help='Regressor: either OLS or QuantReg',
                        choices=['OLS', 'QuantReg'])

    args = parser.parse_args()
    return args


def rank_INT(x, c=3. / 8):
    """Rank-based Inverse Normal Transform.
       Ties share the same value after transformation."""
    n = len(x)
    r = ss.rankdata(x, method='average')
    return ss.norm.ppf((r - c) / (n - 2 * c + 1))


def inverse_normal_transform(df):
    """ apply inverse normal transform on each gene
        Argument:
            df -> pd.DataFrame
        Return
            pd.DataFrame
    """
    return df.apply(rank_INT, axis=1, result_type='expand')


def read_expr(fn):
    expr = pd.read_csv(fn, index_col=0)
    if args.int:
        expr = inverse_normal_transform(expr)
    return expr


def write_output(fit, fout, fields):
    line = "\t".join(fields)
    fout.write(line + '\n')


if __name__ == '__main__':
    args = parse_arguments()

    expr = read_expr(args.expr)
    covar = pd.read_csv(args.covar)
    variants = pd.read_csv(args.variants)
    outputFile = open(args.output, 'w')
    outputFile.write('gene_id\t' + 'variant_id\t' + 'pvals\t' + 'slope\t' + 'tvals\n')

    if args.model == 'OLS':
        lm = sm.OLS
    if args.model == 'QuantReg':
        lm = sm.QuantReg

    with warnings.catch_warnings():
        # Hide annoying warning: IterationLimitWarning: Maximum number of iterations (50) reached.
        warnings.filterwarnings("ignore")
        for idx, row in variants.iterrows():
            Y = expr.loc[row['gene_id']].values
            # covar.T.values[1:, :] => removed the header
            X = np.c_[covar.T.values[1:, :], row.filter(like='GT')]
            X = sm.add_constant(X).astype('float')  # add intercept

            mod = lm(Y, X)

            if lm is sm.QuantReg:
                fit = mod.fit(max_iter=50)
            else:
                fit = mod.fit()

            fields = [row['gene_id'], row['variant_id'], str(
                fit.pvalues[-1]), str(fit.params[-1]), str(fit.tvalues[-1])]
            write_output(fit, outputFile, fields)

            if (idx + 1) % 20 == 0:
                print(f'Finished for {idx+1} pairs.')

    outputFile.close()
