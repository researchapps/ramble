# Copyright 2022-2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

import os
import pytest

import ramble.workspace
import ramble.experiment_set
import ramble.renderer
from ramble.application import ChainCycleDetectedError, InvalidChainError
from ramble.main import RambleCommand

pytestmark = pytest.mark.usefixtures('mutable_config',
                                     'mutable_mock_workspace_path',
                                     'mutable_mock_repo',
                                     )

workspace  = RambleCommand('workspace')


def test_single_experiment_in_set(mutable_mock_workspace_path):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'n_ranks': '{processes_per_node}*{n_nodes}',
            'mpi_command': '',
            'batch_submit': ''
        }

        wl_name = 'test_wl'
        wl_vars = {
            'wl_var1': '1',
            'wl_var2': '2',
            'processes_per_node': '2'
        }
        exp_name = 'series1_{n_ranks}'
        exp_vars = {
            'exp_var1': '1',
            'exp_var2': '2',
            'n_nodes': '2',
        }

        exp_set.set_application_context(app_name, app_vars, None, None, None, None)
        exp_set.set_workload_context(wl_name, wl_vars, None, None, None, None)
        exp_set.set_experiment_context(exp_name, exp_vars, None, None, None, None, None)
        exp_set.build_experiment_chains()

        assert 'basic.test_wl.series1_4' in exp_set.experiments.keys()


def test_vector_experiment_in_set(mutable_mock_workspace_path):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'n_ranks': '{processes_per_node}*{n_nodes}',
            'mpi_command': '',
            'batch_submit': ''
        }

        wl_name = 'test_wl'
        wl_vars = {
            'wl_var1': '1',
            'wl_var2': '2',
            'processes_per_node': '2'
        }
        exp_name = 'series1_{n_ranks}'
        exp_vars = {
            'exp_var1': '1',
            'exp_var2': '2',
            'n_nodes': ['2', '4']
        }

        exp_set.set_application_context(app_name, app_vars, None, None, None, None)
        exp_set.set_workload_context(wl_name, wl_vars, None, None, None, None)
        exp_set.set_experiment_context(exp_name, exp_vars, None, None, None, None, None)
        exp_set.build_experiment_chains()

        assert 'basic.test_wl.series1_4' in exp_set.experiments.keys()
        assert 'basic.test_wl.series1_8' in exp_set.experiments.keys()


def test_nonunique_vector_errors(mutable_mock_workspace_path, capsys):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'n_ranks': '{processes_per_node}*{n_nodes}',
            'mpi_command': '',
            'batch_submit': ''
        }

        wl_name = 'test_wl'
        wl_vars = {
            'wl_var1': '1',
            'wl_var2': '2',
            'processes_per_node': '2'
        }
        exp_name = 'series1_{preocesses_per_node}'
        exp_vars = {
            'exp_var1': '1',
            'exp_var2': '2',
            'n_nodes': ['2', '4']
        }

        exp_set.set_application_context(app_name, app_vars, None, None, None, None)
        exp_set.set_workload_context(wl_name, wl_vars, None, None, None, None)
        with pytest.raises(SystemExit):
            exp_set.set_experiment_context(exp_name, exp_vars, None, None, None, None, None)
            captured = capsys.readouterr()
            assert "is not unique." in captured


def test_zipped_vector_experiments(mutable_mock_workspace_path):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'n_ranks': '{processes_per_node}*{n_nodes}',
            'mpi_command': '',
            'batch_submit': ''
        }

        wl_name = 'test_wl'
        wl_vars = {
            'wl_var1': '1',
            'wl_var2': '2',
            'processes_per_node': ['2', '4']
        }
        exp_name = 'series1_{n_ranks}_{processes_per_node}'
        exp_vars = {
            'exp_var1': '1',
            'exp_var2': '2',
            'n_nodes': ['2', '4']
        }

        exp_set.set_application_context(app_name, app_vars, None, None, None, None)
        exp_set.set_workload_context(wl_name, wl_vars, None, None, None, None)
        exp_set.set_experiment_context(exp_name, exp_vars, None, None, None, None, None)
        exp_set.build_experiment_chains()

        assert 'basic.test_wl.series1_4_2' in exp_set.experiments.keys()
        assert 'basic.test_wl.series1_16_4' in exp_set.experiments.keys()


def test_matrix_experiments(mutable_mock_workspace_path):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'n_ranks': '{processes_per_node}*{n_nodes}',
            'mpi_command': '',
            'batch_submit': ''
        }

        wl_name = 'test_wl'
        wl_vars = {
            'wl_var1': '1',
            'wl_var2': '2',
            'processes_per_node': '2'
        }
        exp_name = 'series1_{n_ranks}'
        exp_vars = {
            'exp_var1': '1',
            'exp_var2': '2',
            'n_nodes': ['2', '3']
        }

        exp_matrices = [
            ['n_nodes']
        ]

        exp_set.set_application_context(app_name, app_vars, None, None, None, None)
        exp_set.set_workload_context(wl_name, wl_vars, None, None, None, None)
        exp_set.set_experiment_context(exp_name, exp_vars, None, exp_matrices, None, None, None)
        exp_set.build_experiment_chains()

        assert 'basic.test_wl.series1_4' in exp_set.experiments.keys()
        assert 'basic.test_wl.series1_6' in exp_set.experiments.keys()


def test_matrix_multiplication_experiments(mutable_mock_workspace_path):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'n_ranks': '{processes_per_node}*{n_nodes}',
            'mpi_command': '',
            'batch_submit': ''
        }

        wl_name = 'test_wl'
        wl_vars = {
            'wl_var1': '1',
            'wl_var2': '2',
            'processes_per_node': ['1', '4', '6']
        }
        exp_name = 'series1_{n_ranks}'
        exp_vars = {
            'exp_var1': '1',
            'exp_var2': '2',
            'n_nodes': ['2', '4']
        }

        exp_matrices = [
            ['n_nodes', 'processes_per_node']
        ]

        exp_set.set_application_context(app_name, app_vars, None, None, None, None)
        exp_set.set_workload_context(wl_name, wl_vars, None, None, None, None)
        exp_set.set_experiment_context(exp_name, exp_vars, None, exp_matrices, None, None, None)
        exp_set.build_experiment_chains()

        assert 'basic.test_wl.series1_2' in exp_set.experiments.keys()
        assert 'basic.test_wl.series1_8' in exp_set.experiments.keys()
        assert 'basic.test_wl.series1_12' in exp_set.experiments.keys()
        assert 'basic.test_wl.series1_4' in exp_set.experiments.keys()
        assert 'basic.test_wl.series1_16' in exp_set.experiments.keys()
        assert 'basic.test_wl.series1_24' in exp_set.experiments.keys()


def test_matrix_vector_experiments(mutable_mock_workspace_path):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'n_ranks': '{processes_per_node}*{n_nodes}',
            'mpi_command': '',
            'batch_submit': ''
        }

        wl_name = 'test_wl'
        wl_vars = {
            'wl_var1': '1',
            'wl_var2': '2',
            'processes_per_node': ['2', '4']
        }
        exp_name = 'series1_{n_ranks}'
        exp_vars = {
            'exp_var1': '1',
            'exp_var2': '2',
            'n_nodes': ['2', '3']
        }

        exp_matrices = [
            ['n_nodes']
        ]

        exp_set.set_application_context(app_name, app_vars, None, None, None, None)
        exp_set.set_workload_context(wl_name, wl_vars, None, None, None, None)
        exp_set.set_experiment_context(exp_name, exp_vars, None, exp_matrices, None, None, None)
        exp_set.build_experiment_chains()

        assert 'basic.test_wl.series1_4' in exp_set.experiments.keys()
        assert 'basic.test_wl.series1_8' in exp_set.experiments.keys()
        assert 'basic.test_wl.series1_6' in exp_set.experiments.keys()
        assert 'basic.test_wl.series1_12' in exp_set.experiments.keys()


def test_multi_matrix_experiments(mutable_mock_workspace_path):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'n_ranks': '{processes_per_node}*{n_nodes}',
            'mpi_command': '',
            'batch_submit': ''
        }

        wl_name = 'test_wl'
        wl_vars = {
            'wl_var1': '1',
            'wl_var2': '2',
            'processes_per_node': ['2', '4']
        }
        exp_name = 'series1_{n_ranks}_{processes_per_node}'
        exp_vars = {
            'exp_var1': '1',
            'exp_var2': '2',
            'n_nodes': ['2', '3']
        }

        exp_matrices = [
            ['n_nodes'],
            ['processes_per_node']
        ]

        exp_set.set_application_context(app_name, app_vars, None, None, None, None)
        exp_set.set_workload_context(wl_name, wl_vars, None, None, None, None)
        exp_set.set_experiment_context(exp_name, exp_vars, None, exp_matrices, None, None, None)
        exp_set.build_experiment_chains()

        assert 'basic.test_wl.series1_4_2' in exp_set.experiments.keys()
        assert 'basic.test_wl.series1_12_4' in exp_set.experiments.keys()


def test_matrix_undefined_var_errors(mutable_mock_workspace_path, capsys):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'n_ranks': '{processes_per_node}*{n_nodes}',
            'mpi_command': '',
            'batch_submit': ''
        }

        wl_name = 'test_wl'
        wl_vars = {
            'wl_var1': '1',
            'wl_var2': '2',
            'processes_per_node': ['2', '4']
        }
        exp_name = 'series1_{n_ranks}_{processes_per_node}'
        exp_vars = {
            'exp_var1': '1',
            'exp_var2': '2',
            'n_nodes': ['2', '3']
        }

        exp_matrices = [
            ['n_nodes'],
            ['foo']
        ]

        exp_set.set_application_context(app_name, app_vars, None, None, None, None)
        exp_set.set_workload_context(wl_name, wl_vars, None, None, None, None)

        with pytest.raises(SystemExit):
            exp_set.set_experiment_context(exp_name, exp_vars, None, exp_matrices,
                                           None, None, None)
            captured = capsys.readouterr()
            assert "variable foo has not been defined yet." in captured


def test_experiment_names_match(mutable_mock_workspace_path):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'n_ranks': '{processes_per_node}*{n_nodes}',
            'mpi_command': '',
            'batch_submit': ''
        }

        wl_name = 'test_wl'
        wl_vars = {
            'wl_var1': '1',
            'wl_var2': '2',
            'processes_per_node': ['2', '4']
        }
        exp_name = 'series1_{n_ranks}_{processes_per_node}'
        exp_vars = {
            'exp_var1': '1',
            'exp_var2': '2',
            'n_nodes': ['2', '3']
        }

        exp_matrices = [
            ['n_nodes'],
            ['processes_per_node']
        ]

        exp_set.set_application_context(app_name, app_vars, None, None, None, None)
        exp_set.set_workload_context(wl_name, wl_vars, None, None, None, None)
        exp_set.set_experiment_context(exp_name, exp_vars, None, exp_matrices, None, None, None)
        exp_set.build_experiment_chains()

        assert 'basic.test_wl.series1_4_2' in exp_set.experiments.keys()
        assert 'basic.test_wl.series1_12_4' in exp_set.experiments.keys()

        for exp, app in exp_set.all_experiments():
            assert exp == app.expander.expand_var('{experiment_namespace}')


def test_cross_experiment_variable_references(mutable_mock_workspace_path):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'n_ranks': '{processes_per_node}*{n_nodes}',
            'mpi_command': '',
            'batch_submit': ''
        }

        wl_name = 'test_wl'
        wl_vars = {
            'wl_var1': '1',
            'wl_var2': '2',
            'processes_per_node': '2'
        }
        exp1_name = 'series1_{n_ranks}'
        exp1_vars = {
            'exp_var1': '1',
            'exp_var2': '2',
            'n_nodes': '2',
            'test_var': 'success'
        }

        exp2_name = 'series2_{n_ranks}'
        exp2_vars = {
            'exp_var1': '1',
            'exp_var2': '2',
            'n_nodes': '2',
            'test_var': 'test_var in basic.test_wl.series1_4'
        }

        exp_set.set_application_context(app_name, app_vars, None, None, None, None)
        exp_set.set_workload_context(wl_name, wl_vars, None, None, None, None)
        exp_set.set_experiment_context(exp1_name, exp1_vars, None, None, None, None, None)
        exp_set.set_experiment_context(exp2_name, exp2_vars, None, None, None, None, None)
        exp_set.build_experiment_chains()

        assert 'basic.test_wl.series1_4' in exp_set.experiments.keys()
        assert 'basic.test_wl.series2_4' in exp_set.experiments.keys()

        exp2_app = exp_set.experiments['basic.test_wl.series2_4']
        assert exp2_app.expander.expand_var('{test_var}') == 'success'


def test_cross_experiment_missing_experiment_errors(mutable_mock_workspace_path):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'n_ranks': '{processes_per_node}*{n_nodes}',
            'mpi_command': '',
            'batch_submit': ''
        }

        wl_name = 'test_wl'
        wl_vars = {
            'wl_var1': '1',
            'wl_var2': '2',
            'processes_per_node': '2'
        }
        exp1_name = 'series1_{n_ranks}'
        exp1_vars = {
            'exp_var1': '1',
            'exp_var2': '2',
            'n_nodes': '2',
            'test_var': 'processes_per_node in basic.test_wl.does_not_exist'
        }

        exp_set.set_application_context(app_name, app_vars, None, None, None, None)
        exp_set.set_workload_context(wl_name, wl_vars, None, None, None, None)
        exp_set.set_experiment_context(exp1_name, exp1_vars, None, None, None, None, None)
        exp_set.build_experiment_chains()

        assert 'basic.test_wl.series1_4' in exp_set.experiments.keys()

        exp1_app = exp_set.experiments['basic.test_wl.series1_4']

        with pytest.raises(ramble.expander.RambleSyntaxError) as e:
            exp1_app.expander.expand_var('{test_var}')
            expected = f'basic.test_wl_does_not_exist does not exist in "{exp1_vars["test_var"]}"'
            assert e.error == expected


def test_n_ranks_correct_defaults(mutable_mock_workspace_path):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'mpi_command': '',
            'batch_submit': ''
        }

        wl_name = 'test_wl'
        wl_vars = {
            'wl_var1': '1',
            'wl_var2': '2',
            'processes_per_node': '2'
        }
        exp_name = 'series1_{n_ranks}'
        exp_vars = {
            'exp_var1': '1',
            'exp_var2': '2',
            'n_nodes': ['2', '3']
        }

        exp_matrices = [
            ['n_nodes']
        ]

        exp_set.set_application_context(app_name, app_vars, None, None, None, None)
        exp_set.set_workload_context(wl_name, wl_vars, None, None, None, None)
        exp_set.set_experiment_context(exp_name, exp_vars, None, exp_matrices, None, None, None)
        exp_set.build_experiment_chains()

        assert 'basic.test_wl.series1_4' in exp_set.experiments.keys()
        assert 'basic.test_wl.series1_6' in exp_set.experiments.keys()


def test_n_nodes_correct_defaults(mutable_mock_workspace_path):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'n_ranks': ['4', '6'],
            'mpi_command': '',
            'batch_submit': ''
        }

        wl_name = 'test_wl'
        wl_vars = {
            'wl_var1': '1',
            'wl_var2': '2',
            'processes_per_node': '2'
        }
        exp_name = 'series1_{n_ranks}_{n_nodes}'
        exp_vars = {
            'exp_var1': '1',
            'exp_var2': '2',
        }

        exp_matrices = [
            ['n_ranks']
        ]

        exp_set.set_application_context(app_name, app_vars, None, None, None, None)
        exp_set.set_workload_context(wl_name, wl_vars, None, None, None, None)
        exp_set.set_experiment_context(exp_name, exp_vars, None, exp_matrices, None, None, None)
        exp_set.build_experiment_chains()

        assert 'basic.test_wl.series1_4_2' in exp_set.experiments.keys()
        assert 'basic.test_wl.series1_6_3' in exp_set.experiments.keys()


def test_processes_per_node_correct_defaults(mutable_mock_workspace_path):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)
        # Remove workspace vars, which default to a `processes_per_node = -1` definition.
        exp_set._variables[exp_set._contexts.workspace] = {}

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'n_ranks': ['4', '6'],
            'mpi_command': '',
            'batch_submit': ''
        }

        wl_name = 'test_wl'
        wl_vars = {
            'wl_var1': '1',
            'wl_var2': '2',
        }
        exp_name = 'series1_{n_ranks}_{processes_per_node}'
        exp_vars = {
            'exp_var1': '1',
            'exp_var2': '2',
            'n_nodes': ['2', '3']
        }

        exp_set.set_application_context(app_name, app_vars, None, None, None, None)
        exp_set.set_workload_context(wl_name, wl_vars, None, None, None, None)
        exp_set.set_experiment_context(exp_name, exp_vars, None, None, None, None, None)
        exp_set.build_experiment_chains()

        assert 'basic.test_wl.series1_4_2' in exp_set.experiments.keys()
        assert 'basic.test_wl.series1_6_2' in exp_set.experiments.keys()


@pytest.mark.parametrize('var', [
    'command', 'spack_env'
])
def test_reserved_keywords_error_in_application(mutable_mock_workspace_path, var, capsys):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'n_ranks': ['4', '6'],
            var: 'should_fail',
            'mpi_command': '',
            'batch_submit': ''
        }

        with pytest.raises(ramble.experiment_set.RambleVariableDefinitionError):
            exp_set.set_application_context(app_name, app_vars, None, None, None, None)
            captured = capsys.readouterr()
            assert "In application basic" in captured
            assert f"{var}" in captured
            assert "is reserved by ramble" in captured


@pytest.mark.parametrize('var', [
    'command', 'spack_env'
])
def test_reserved_keywords_error_in_workload(mutable_mock_workspace_path, var, capsys):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'n_ranks': ['4', '6'],
            'mpi_command': '',
            'batch_submit': ''
        }

        wl_name = 'test_wl'
        wl_vars = {
            'wl_var1': '1',
            'wl_var2': '2',
            var: 'should_fail'
        }

        exp_set.set_application_context(app_name, app_vars, None, None, None, None)
        with pytest.raises(ramble.experiment_set.RambleVariableDefinitionError):
            exp_set.set_workload_context(wl_name, wl_vars, None, None, None, None)
            captured = capsys.readouterr()
            assert "In workload basic.test_wl" in captured
            assert f"{var}" in captured
            assert "is reserved by ramble" in captured


@pytest.mark.parametrize('var', [
    'command', 'spack_env'
])
def test_reserved_keywords_error_in_experiment(mutable_mock_workspace_path, var, capsys):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)
        # Remove workspace vars, which default to a `processes_per_node = -1` definition.
        exp_set._variables[exp_set._contexts.base] = {}

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'n_ranks': ['4', '6'],
            'mpi_command': '',
            'batch_submit': ''
        }

        wl_name = 'test_wl'
        wl_vars = {
            'wl_var1': '1',
            'wl_var2': '2',
        }
        exp_name = 'series1_{n_ranks}_{processes_per_node}'
        exp_vars = {
            'exp_var1': '1',
            'exp_var2': '2',
            'n_nodes': ['2', '3'],
            var: 'should_fail'
        }

        exp_set.set_application_context(app_name, app_vars, None, None, None, None)
        exp_set.set_workload_context(wl_name, wl_vars, None, None, None, None)
        with pytest.raises(ramble.experiment_set.RambleVariableDefinitionError):
            exp_set.set_experiment_context(exp_name, exp_vars, None, None, None, None, None)
            captured = capsys.readouterr()
            assert "In experiment basic.test_wl.series1_{n_ranks}_{processes_per_node}" in captured
            assert f"{var}" in captured
            assert "is reserved by ramble" in captured


@pytest.mark.parametrize('var', [
    'batch_submit', 'mpi_command'
])
def test_missing_required_keyword_errors(mutable_mock_workspace_path, var, capsys):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)
        for context in exp_set._contexts:
            if exp_set._variables[context] and var in exp_set._variables[context]:
                del exp_set._variables[context][var]

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'n_ranks': ['4', '6'],
        }

        wl_name = 'test_wl'
        wl_vars = {
            'wl_var1': '1',
            'wl_var2': '2',
        }
        exp_name = 'series1_{n_ranks}_{processes_per_node}'
        exp_vars = {
            'exp_var1': '1',
            'exp_var2': '2',
            'n_nodes': ['2', '3'],
            'batch_submit': '',
            'mpi_command': ''
        }

        if var in exp_vars.keys():
            del exp_vars[var]

        exp_set.set_application_context(app_name, app_vars, None, None, None, None)
        exp_set.set_workload_context(wl_name, wl_vars, None, None, None, None)
        with pytest.raises(ramble.experiment_set.RambleVariableDefinitionError):
            exp_set.set_experiment_context(exp_name, exp_vars, None, None, None, None, None)
            captured = capsys.readouterr()
            assert f'Required key "{var}" is not defined' in captured.err
            assert 'One or more required keys are not defined within an experiment.' \
                in captured.err
            assert "In experiment basic.test_wl.series1_{n_ranks}_{processes_per_node}" \
                in captured.err


def test_chained_experiments_populate_new_experiments(mutable_mock_workspace_path, capsys):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'processes_per_node': '1',
            'mpi_command': '',
            'batch_submit': ''
        }

        wl_name = 'test_wl'
        wl_vars = {
            'wl_var1': '1',
            'wl_var2': '2',
        }
        exp1_name = 'test1'
        exp1_vars = {
            'n_ranks': '2'
        }
        exp2_name = 'series2_{n_ranks}'
        exp2_vars = {
            'exp_var1': '1',
            'exp_var2': '2',
            'n_ranks': ['4', '6']
        }
        exp2_chains = [
            {
                'name': 'basic.test_wl.test1',
                'order': 'before_root',
                'command': '{execute_experiment}',
                'variables': {}
            },
            {
                'name': 'basic.test_wl.test1',
                'order': 'after_root',
                'command': '{execute_experiment}',
                'variables': {}
            }
        ]

        exp_set.set_application_context(app_name, app_vars, None, None, None, None)
        exp_set.set_workload_context(wl_name, wl_vars, None, None, None, None)
        exp_set.set_experiment_context(exp1_name, exp1_vars, None, None, None, None, None)
        exp_set.set_experiment_context(exp2_name, exp2_vars, None, None, None, None, exp2_chains)
        exp_set.build_experiment_chains()

        assert 'basic.test_wl.series2_4' in \
            exp_set.experiments
        assert 'basic.test_wl.series2_4.chain.0.basic.test_wl.test1' in \
            exp_set.chained_experiments
        assert 'basic.test_wl.series2_4.chain.1.basic.test_wl.test1' in \
            exp_set.chained_experiments
        assert 'basic.test_wl.series2_6' in \
            exp_set.experiments
        assert 'basic.test_wl.series2_6.chain.0.basic.test_wl.test1' in \
            exp_set.chained_experiments
        assert 'basic.test_wl.series2_6.chain.1.basic.test_wl.test1' in \
            exp_set.chained_experiments
        assert 'basic.test_wl.test1' in exp_set.experiments


def test_chained_experiment_has_correct_directory(mutable_mock_workspace_path, capsys):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'processes_per_node': '1',
            'mpi_command': '',
            'batch_submit': ''
        }

        wl_name = 'test_wl'
        wl_vars = {
            'wl_var1': '1',
            'wl_var2': '2',
        }
        exp1_name = 'test1'
        exp1_vars = {
            'n_ranks': '2'
        }
        exp2_name = 'series2_{n_ranks}'
        exp2_vars = {
            'exp_var1': '1',
            'exp_var2': '2',
            'n_ranks': '4'
        }
        exp2_chains = [
            {
                'name': 'basic.test_wl.test1',
                'order': 'before_root',
                'command': '{execute_experiment}',
                'variables': {}
            },
        ]

        exp_set.set_application_context(app_name, app_vars, None, None, None, None)
        exp_set.set_workload_context(wl_name, wl_vars, None, None, None, None)
        exp_set.set_experiment_context(exp1_name, exp1_vars, None, None, None, None, None)
        exp_set.set_experiment_context(exp2_name, exp2_vars, None, None, None, None, exp2_chains)
        exp_set.build_experiment_chains()

        parent_name = 'basic.test_wl.series2_4'
        chained_name = 'basic.test_wl.series2_4.chain.0.basic.test_wl.test1'
        chained_dir = '0.basic.test_wl.test1'
        assert parent_name in exp_set.experiments
        assert chained_name in exp_set.chained_experiments

        parent_inst = exp_set.get_experiment(parent_name)
        chained_inst = exp_set.get_experiment(chained_name)

        parent_run_dir = parent_inst.expander.expand_var('{experiment_run_dir}')
        expected_dir = os.path.join(parent_run_dir, 'chained_experiments', chained_dir)
        assert chained_inst.variables['experiment_run_dir'] == expected_dir


def test_chained_cycle_errors(mutable_mock_workspace_path, capsys):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'processes_per_node': '1',
            'mpi_command': '',
            'batch_submit': ''
        }

        wl_name = 'test_wl'
        wl_vars = {
            'wl_var1': '1',
            'wl_var2': '2',
        }
        exp1_name = 'test1'
        exp1_vars = {
            'n_ranks': '2'
        }
        exp2_name = 'series2_{n_ranks}'
        exp2_vars = {
            'exp_var1': '1',
            'exp_var2': '2',
            'n_ranks': '4'
        }
        exp2_chains = [
            {
                'name': 'basic.test_wl.series2_4',
                'order': 'before_root',
                'command': '{execute_experiment}',
                'variables': {}
            },
        ]

        exp_set.set_application_context(app_name, app_vars, None, None, None, None)
        exp_set.set_workload_context(wl_name, wl_vars, None, None, None, None)
        exp_set.set_experiment_context(exp1_name, exp1_vars, None, None, None, None, None)
        exp_set.set_experiment_context(exp2_name, exp2_vars, None, None, None, None, exp2_chains)
        with pytest.raises(ChainCycleDetectedError):
            exp_set.build_experiment_chains()
            captured = capsys.readouterr
            assert "Cycle detected in experiment chain" in captured


def test_chained_invalid_order_errors(mutable_mock_workspace_path, capsys):
    workspace('create', 'test')

    assert 'test' in workspace('list')

    with ramble.workspace.read('test') as ws:
        exp_set = ramble.experiment_set.ExperimentSet(ws)

        app_name = 'basic'
        app_vars = {
            'app_var1': '1',
            'app_var2': '2',
            'processes_per_node': '1',
            'mpi_command': '',
            'batch_submit': ''
        }

        wl_name = 'test_wl'
        wl_vars = {
            'wl_var1': '1',
            'wl_var2': '2',
        }
        exp1_name = 'test1'
        exp1_vars = {
            'n_ranks': '2'
        }
        exp2_name = 'series2_{n_ranks}'
        exp2_vars = {
            'exp_var1': '1',
            'exp_var2': '2',
            'n_ranks': '4'
        }
        exp2_chains = [
            {
                'name': 'basic.test_wl.test1',
                'order': 'foo',
                'command': '{execute_experiment}',
                'variables': {}
            },
        ]

        exp_set.set_application_context(app_name, app_vars, None, None, None, None)
        exp_set.set_workload_context(wl_name, wl_vars, None, None, None, None)
        exp_set.set_experiment_context(exp1_name, exp1_vars, None, None, None, None, None)
        exp_set.set_experiment_context(exp2_name, exp2_vars, None, None, None, None, exp2_chains)
        with pytest.raises(InvalidChainError):
            exp_set.build_experiment_chains()
            captured = capsys.readouterr
            assert "Invalid experiment chain defined:" in captured
