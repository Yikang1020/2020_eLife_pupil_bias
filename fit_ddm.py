import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from joblib import Parallel, delayed
from IPython import embed as shell

from accumodels import plot_tools, pyddm_tools
from analyses_tools import *

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
sns.set(style='ticks', font='Arial', font_scale=1, rc={
    'axes.labelsize': 7,
    'axes.titlesize': 7,
    'xtick.labelsize': 6,
    'ytick.labelsize': 6,
    'legend.fontsize': 6,
    'axes.linewidth': 0.25,
    'xtick.major.width': 0.25,
    'ytick.major.width': 0.25,
    'ytick.major.width': 0.25,
    'ytick.major.width': 0.25,
    'ytick.major.pad' : 2.0,
    'ytick.minor.pad' : 2.0,
    'xtick.major.pad' : 2.0,
    'xtick.minor.pad' : 2.0,
    'axes.labelpad' : 4.0,
    'axes.titlepad' : 6.0,
    } )
sns.plotting_context()

# all model elements:
# -------------------

project_dir = '/home/jwdegee/repos/2020_eLife_pupil_bias/'
# experiment_names = ['yesno_audio', 'bias_manipulation_30', 'bias_manipulation_70']
experiment_names = ['yesno_audio', 'bias_manipulation']
bin_measures = ['pupil_resp_1s', 'pupil_resp_1s', 'pupil_resp_1s']
nrs_bins = [5,3]

n_jobs = 25
fit_model = 1
# versions = [9,8,7,6,5,4,3,2,1,0]
# versions = [4,3,2,1,0]
versions = [9,8,7,6,5]
# versions = [6,7]
# versions = [8,9]
# versions = [1,2,3,4]
# versions = [0]

# for analyse_exp in [0,1,2]:
for analyse_exp in [1]:

    experiment_name, bin_measure, n_bins = experiment_names[analyse_exp], bin_measures[analyse_exp], nrs_bins[analyse_exp]

    # set options:
    if experiment_name == 'bias_manipulation':
            model_settings = [
            {'urgency':True, 'T_dur':3, 'depends_on': {'a':['bin'], 'u':None,    'v':['bin'], 't':['bin'], 'z':['cons', 'bin'], 'b':['cons', 'bin']}},
            {'urgency':True, 'T_dur':3, 'depends_on': {'a':None,    'u':None,    'v':None,    't':None,    'z':['cons', 'bin'], 'b':['cons', 'bin']}},
            {'urgency':True, 'T_dur':3, 'depends_on': {'a':None,    'u':None,    'v':None,    't':None,    'z':['cons', 'bin'], 'b':['cons']       }},
            {'urgency':True, 'T_dur':3, 'depends_on': {'a':None,    'u':None,    'v':None,    't':None,    'z':['cons'],        'b':['cons', 'bin']}},
            {'urgency':True, 'T_dur':3, 'depends_on': {'a':None,    'u':['bin'], 'v':None,    't':None,    'z':['cons'],        'b':['cons']       }},

            {'urgency':False, 'T_dur':3, 'depends_on': {'a':['bin'], 'u':None,    'v':['bin'], 't':['bin'], 'z':['cons', 'bin'], 'b':['cons', 'bin']}},
            {'urgency':False, 'T_dur':3, 'depends_on': {'a':None,    'u':None,    'v':None,    't':None,    'z':['cons', 'bin'], 'b':['cons', 'bin']}},
            {'urgency':False, 'T_dur':3, 'depends_on': {'a':None,    'u':None,    'v':None,    't':None,    'z':['cons', 'bin'], 'b':['cons']       }},
            {'urgency':False, 'T_dur':3, 'depends_on': {'a':None,    'u':None,    'v':None,    't':None,    'z':['cons'],        'b':['cons', 'bin']}},
            {'urgency':True, 'T_dur':3, 'depends_on': {'a':None,     'u':['bin'], 'v':None,    't':None,    'z':['cons'],        'b':['cons']       }},
            ]
    else:
        model_settings = [
            {'urgency':True, 'T_dur':3, 'depends_on': {'a':['bin'],  'u':None,    'v':['bin'], 't':['bin'], 'z':['bin'], 'b':['bin']}},
            {'urgency':True, 'T_dur':3, 'depends_on': {'a':None,     'u':None,    'v':None,    't':None,    'z':['bin'], 'b':['bin']}},
            {'urgency':True, 'T_dur':3, 'depends_on': {'a':None,     'u':None,    'v':None,    't':None,    'z':['bin'], 'b':None   }},
            {'urgency':True, 'T_dur':3, 'depends_on': {'a':None,     'u':None,    'v':None,    't':None,    'z':None,    'b':['bin']}},
            {'urgency':True, 'T_dur':3, 'depends_on': {'a':None,     'u':['bin'], 'v':None,    't':None,    'z':None,    'b':None   }},

            {'urgency':False, 'T_dur':3, 'depends_on': {'a':['bin'], 'u':None,    'v':['bin'], 't':['bin'], 'z':['bin'], 'b':['bin']}},
            {'urgency':False, 'T_dur':3, 'depends_on': {'a':None,    'u':None,    'v':None,    't':None,    'z':['bin'], 'b':['bin']}},
            {'urgency':False, 'T_dur':3, 'depends_on': {'a':None,    'u':None,    'v':None,    't':None,    'z':['bin'], 'b':None   }},
            {'urgency':False, 'T_dur':3, 'depends_on': {'a':None,    'u':None,    'v':None,    't':None,    'z':None,    'b':['bin']}},
            {'urgency':True, 'T_dur':3, 'depends_on': {'a':None,     'u':['bin'], 'v':None,    't':None,    'z':None,    'b':None   }},
            ]

    # load data:
    if experiment_name == 'bias_manipulation':
        df = pd.concat((pd.read_csv(os.path.join(project_dir, 'data', 'ddm', '{}_30.csv'.format(experiment_name))),
                        pd.read_csv(os.path.join(project_dir, 'data', 'ddm', '{}_70.csv'.format(experiment_name))))).reset_index(drop=True)
        df['cons'] = df['signal_probability'].copy()
        df['cons'] = (df['cons']<50).astype(int)
        df['bin'] = df.groupby(['subj_idx', 'cons'])[bin_measure].apply(pd.qcut, q=n_bins, labels=False)
    else:
        df = pd.read_csv(os.path.join(project_dir, 'data', 'ddm', '{}.csv'.format(experiment_name)))
        df['bin'] = df.groupby(['subj_idx'])[bin_measure].apply(pd.qcut, q=n_bins, labels=False)

    # fix columns:
    df.loc[df['stimulus']==0, 'stimulus'] = -1

    # Remove short and long RTs:
    # df = df[df["rt"] > .1] # Remove trials less than 100ms
    # df = df[df["rt"] < 3] # Remove trials greater than 1650ms

    # loop across model versions:
    bics = []
    resids = []
    for version in versions:

        # cut dataframe:
        if experiment_name == 'bias_manipulation':
            df_emp = df.loc[:,['subj_idx', 'response', 'rt', 'stimulus', 'correct', 'cons', 'bin', bin_measure]]
        else:
            df_emp = df.loc[:,['subj_idx', 'response', 'rt', 'stimulus', 'correct', 'bin', bin_measure]]

        if fit_model:
            # fit model:
            res = Parallel(n_jobs=n_jobs, verbose=1, backend='loky')(delayed(pyddm_tools.fit_model)(data, model_settings[version]) 
                                        for subj_idx, data in df_emp.groupby(['subj_idx']))
            # params:
            model_nr = 0
            params = []
            for subj_idx, data in df_emp.groupby(['subj_idx']):
                param_names = []
                for component in res[model_nr].dependencies: 
                    param_names = param_names + component.required_parameters
                pars = pd.DataFrame(np.atleast_2d([p.real for p in res[model_nr].get_model_parameters()]), columns=param_names)
                pars['bic'] = res[model_nr].fitresult.value() 
                pars['subj_idx'] = subj_idx
                params.append(pars)
                model_nr += 1
            params = pd.concat(params).reset_index(drop=True)
            
            # .melt(id_vars=['subj_idx'])
            # params['bin'] = np.array([int(c[-1]) if c[-1].isnumeric() else None for c in params['variable']])
            # params['variable'] = np.array([c[:-1] if c[-1].isnumeric() else c for c in params['variable']])
            
            # save:
            params.to_csv(os.path.join(project_dir, 'fits', '{}_{}.csv'.format(experiment_name, version)))

        else:
            
            # load:
            params = pd.read_csv(os.path.join(project_dir, 'fits', '{}_{}.csv'.format(experiment_name, version)))
            params[bin_measure] = np.NaN
            for (v, b), params_cut in params.groupby(['variable', 'bin']):
                if len(params_cut.index) == len(params['subj_idx'].unique()):
                    params.loc[params_cut.index, bin_measure] = np.array(df_emp.groupby(['subj_idx', 'bin']).mean().reset_index().query('bin=={}'.format(b))[bin_measure])

            # empirical SDT:
            sdt_emp = compute_behavior(df=df_emp, groupby=['subj_idx', 'bin']).melt(id_vars=['subj_idx', 'bin'])
            sdt_emp[bin_measure] = np.NaN
            for (v, b), params_cut in sdt_emp.groupby(['variable', 'bin']):
                if len(params_cut.index) == len(sdt_emp['subj_idx'].unique()):
                    sdt_emp.loc[params_cut.index, bin_measure] = np.array(df_emp.groupby(['subj_idx', 'bin']).mean().reset_index().query('bin=={}'.format(b))[bin_measure])

            # fig = plt.figure(figsize=(2,2))
            # delta_c = np.array(sdt_emp.loc[(sdt_emp['variable']=='c')&(sdt_emp['bin']==1), 'value']) - np.array(sdt_emp.loc[(sdt_emp['variable']=='c')&(sdt_emp['bin']==0), 'value'])
            # param_bins = [p.split('_')[0] for p in model_settings[version].keys() if ('_bin' in p) & model_settings[version][p]]
            # for p in param_bins:
            #     delta_param = np.array(sdt_emp.loc[(params['variable']==p)&(sdt_emp['bin']==1), 'value']) - np.array(sdt_emp.loc[(params['variable']==p)&(sdt_emp['bin']==0), 'value'])
            #     sns.regplot(delta_c, delta_param)
            #     print(sp.stats.pearsonr(delta_c, delta_param))
            # fig.savefig(os.path.join(project_dir, 'figs', 'ddm', '{}_{}_param_correlation.pdf'.format(experiment_name, version)))

            # simulate data:
            df_sim = pd.concat(Parallel(n_jobs=n_jobs, verbose=1, backend='loky')(delayed(pyddm_tools.simulate_data)(data, params, model_settings[version], subj_idx, 100000)
                                for subj_idx, data in df_emp.groupby(['subj_idx']))).reset_index()

            # simulated SDT:
            sdt_sim = compute_behavior(df=df_sim, groupby=['subj_idx', 'bin']).melt(id_vars=['subj_idx', 'bin'])
            sdt_sim[bin_measure] = np.NaN
            for (v, b), params_cut in sdt_sim.groupby(['variable', 'bin']):
                if len(params_cut.index) == len(sdt_sim['subj_idx'].unique()):
                    sdt_sim.loc[params_cut.index, bin_measure] = np.array(df_emp.groupby(['subj_idx', 'bin']).mean().reset_index().query('bin=={}'.format(b))[bin_measure])

            # # summary plot:
            # for b in range(n_bins):
            #     fig = plot_tools.summary_plot_group(df_emp.loc[df['bin']==b,:], df_sim.loc[df_sim['bin']==b,:])
            #     fig.savefig(os.path.join(project_dir, 'figs', 'ddm', '{}_{}_model_fit_{}.pdf'.format(experiment_name, version, b)))
            
            # if not model_settings[version]['pool']:

            #     # analysis:
            #     fig = mixed_linear_modeling(sdt_emp, x='bin', df_sim=sdt_sim,)
            #     fig.savefig(os.path.join(project_dir, 'figs', 'ddm', '{}_{}_sdt_bars.pdf'.format(experiment_name, version)))

            #     # analysis:
            #     fig = mixed_linear_modeling(params.loc[~pd.isnull(params['bin']),:], x='bin')
            #     # fig = mixed_linear_modeling(params.loc[~pd.isnull(params['bin']),:], x=bin_measure)
            #     fig.savefig(os.path.join(project_dir, 'figs', 'ddm', '{}_{}_bars.pdf'.format(experiment_name, version)))

            # resid:
            resid = pd.DataFrame(sdt_emp.loc[sdt_emp['variable']=='c', ['subj_idx', 'bin', 'value']]).reset_index(drop=True)
            resid['value'] = (resid['value'] - np.array(sdt_sim.loc[sdt_emp['variable']=='c', 'value']))**2
            resid['model'] = version
            resids.append(resid)

            # bics:
            bic = pd.DataFrame(params.loc[params['variable']=='bic', ['subj_idx', 'value']]).reset_index(drop=True)
            bic['model'] = version
            bics.append(bic)

    if not fit_model:

        resids = pd.concat(resids)
        bics = pd.concat(bics)
        print()
        print(experiment_name)
        print(bics.groupby('model').mean())
        print(resids.groupby('model').mean())

        bics = bics.loc[bics['model']!=0,:]
        bics = bics.loc[bics['model']!=5,:]

        subtract = np.array(bics.loc[bics['model']==bics['model'].min(), 'value'])
        for m in bics['model'].unique():
            bics.loc[bics['model']==m, 'value'] = np.array(bics.loc[bics['model']==m, 'value']) - subtract
        fig = plt.figure(figsize=(1.5,1.5))
        sns.barplot(x='model', y='value', units='subj_idx', ci=None, data=bics)
        sns.stripplot(x='model', y='value', color='grey', size=2, data=bics)
        plt.xticks([0,1,2,3], ['z+dc', 'z', 'dc', 'u'])
        plt.ylabel('Δ BIC')
        sns.despine(offset=2, trim=True)
        plt.tight_layout()
        fig.savefig(os.path.join(project_dir, 'figs', 'ddm', '{}_{}_bics.pdf'.format(experiment_name, version)))

        fig = plt.figure(figsize=(1.5,1.5))
        sns.barplot(x='model', y='value', units='subj_idx', ci=66, data=bics)
        # sns.stripplot(x='model', y='value', color='grey', data=bics)
        plt.xticks([0,1,2,3], ['z+dc', 'z', 'dc', 'u'])
        plt.ylabel('Δ BIC')
        sns.despine(offset=2, trim=True)
        plt.tight_layout()
        fig.savefig(os.path.join(project_dir, 'figs', 'ddm', '{}_{}_bics2.pdf'.format(experiment_name, version)))