## eQTL-mapping with Quantile Regression

## FastQTL

This repository contains runnable python scripts which perform eQTL mapping with OLS/Quantile Regression, with an optional inverse-normal-transformation (INT). The input files here are supposed to be well-structured in csv format, just for the purpose of demonstrate quantile regression.

1. Input the expression matrix, covariates, variants genotype.
2. `--int` Turn on inverse-normal-transformation to normalize gene expression to a Gaussian distribution if needed
3. Select regressor: either OLS or QuantReg.
4. Output the p-value, slope, and t-value of coefficient for genotype.

This repository serves as a supplementary for the manuscripts submitted to Briefs in Bioinformatics. see: http://

#### Usage

Quantile Regression without inverse-normal-transformation.  
`python eQTL_mapping.py data/expr_TPM.csv data/covariates.csv data/variant_genotype.csv output/test_output.txt --model QuantReg`

OLS with inverse-normal-transformation (OLS is sensitive to outliers, so it is wise to turn on INT)  
`python eQTL_mapping.py data/expr_TPM.csv data/covariates.csv data/variant_genotype.csv output/test_output.txt --model OLS --int`

Use `python eQTL_mapping.py -h` to see complete options list.
