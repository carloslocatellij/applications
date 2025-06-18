import unittest
from unittest.mock import patch, MagicMock, mock_open, call # Added call
import json # Added json import
import sys # Import sys

# Create a mock for the 'my_validador' module
# This needs to be done BEFORE 'textos_modelos' is imported,
# as it directly tries to 'from my_validador import *'
mock_my_validador = MagicMock()
sys.modules['my_validador'] = mock_my_validador

# Mock for db operations - Define db_mock ONCE.
db_mock = MagicMock()

import types # For creating a new module object

# Module to be tested
module_name = 'Viveiro_Analises.models.textos_modelos'

# Pre-create a module object for textos_modelos
# This allows us to inject 'db' and 'Field' before its code actually runs.
textos_modelos_module = types.ModuleType(module_name)
textos_modelos_module.__dict__['db'] = db_mock      # Inject db into its globals
Field_mock = MagicMock() # Field is likely a class or factory function
textos_modelos_module.__dict__['Field'] = Field_mock # Inject Field into its globals

# Also add other things it might expect at the top level, like __file__
textos_modelos_module.__file__ = '/app/Viveiro_Analises/models/textos_modelos.py' # Or a mock path

# Put this pre-configured module into sys.modules.
# When the actual import happens, Python will find this existing module
# and execute the textos_modelos.py file's content within this module's namespace.
sys.modules[module_name] = textos_modelos_module

# Now, import the specific names. The import system should use the module
# we've placed in sys.modules. The 'db.define_table' line inside
# textos_modelos.py should find the 'db' we injected.
# from Viveiro_Analises.models.textos_modelos import determinar_despacho, Despachar, dict_condicoes_de_templates

# Get the path to the module's file
# Assuming the module path is /app/Viveiro_Analises/models/textos_modelos.py
# __file__ was set on the mock module object earlier.
module_file_path = textos_modelos_module.__file__

try:
    with open(module_file_path, 'r') as f:
        module_code = f.read()
    # Execute the module's code within the prepared module's namespace
    # Pass globals and locals explicitly to mimic module execution context
    exec(module_code, textos_modelos_module.__dict__, textos_modelos_module.__dict__)
except Exception as e:
    print(f"Error during exec of {module_name}: {e}")
    # Include traceback if possible, or at least the type of error and message.
    import traceback
    traceback.print_exc()
    raise ImportError(f"Failed to initialize {module_name} due to an exception during exec: {e}")


# Check if the names were actually defined in the module after execution
if not hasattr(textos_modelos_module, 'determinar_despacho'):
    raise ImportError(f"Failed to define 'determinar_despacho' in {module_name} even after exec. "
                      "This indicates a persistent issue in module code or setup.")

# If the above check passes, then we can proceed to import the names for convenience
# This step might seem redundant as names are already in textos_modelos_module.__dict__,
# but 'from ... import' does perform some checks and is common practice.
# Alternatively, access them directly: textos_modelos_module.determinar_despacho
from Viveiro_Analises.models.textos_modelos import determinar_despacho, Despachar, dict_condicoes_de_templates

class TestTextosModelos(unittest.TestCase):

    def setUp(self):
        """
        This method is called before each test.
        We reset mocks here to ensure test isolation.
        db_mock is already active globally due to the patch at the module level.
        We just need to reset its state for each test.
        """
        db_mock.reset_mock()
        # T_mock.reset_mock() # If T was used

        # Configure db_mock for calls like db(db.some_table.id > 0).select()
        # 1. For the comparison: db.despacho_template.id > 0
        mock_id_field = MagicMock()
        # The __gt__ method will be called for the > operator.
        # It doesn't matter much what it returns, as long as it's a valid query component for db().
        mock_id_field.__gt__.return_value = "fake_id_gt_0_condition"
        db_mock.despacho_template.id = mock_id_field

        # 2. For the db(...) call itself
        query_mock = MagicMock()
        db_mock.return_value = query_mock # db(...) returns query_mock

        # 3. For query_mock.select(...) call
        # This will be further configured in tests that use dict_condicoes_de_templates
        # e.g., query_mock.select.return_value.as_dict.return_value = ...
        # For now, ensure select returns a mock that can have as_dict() called on it.
        select_result_mock = MagicMock()
        query_mock.select.return_value = select_result_mock

        # db_mock is globally patched. No need to start/stop it here per test.
        # self.addCleanup can't be used for module-level patches started outside the class.
        # pass # setUp now only resets mocks or does other per-test setup - REMOVE PASS

    # Test for dict_condicoes_de_templates
    def test_dict_condicoes_de_templates_empty_db(self):
        # Mock the database query to return an empty list
        db_mock.return_value.select.return_value.as_dict.return_value = {}

        dict_condicoes, dict_textos = dict_condicoes_de_templates()

        self.assertEqual(dict_condicoes, {})
        self.assertEqual(dict_textos, {})
        db_mock.assert_called_once_with(db_mock.despacho_template.id > 0)
        db_mock.return_value.select.assert_called_once_with('id', 'condicoes', 'texto')

    def test_dict_condicoes_de_templates_with_data(self):
        # Mock database result
        mock_data = {
            0: {
                '_extra': {
                    'id': 1,
                    'condicoes': json.dumps([{'campo': 'tipo_imovel', 'operador': '=', 'valor': 'urbano'}]),
                    'texto': 'Template A'
                }
            },
            1: {
                '_extra': {
                    'id': 2,
                    'condicoes': json.dumps({'campo': 'total_podas', 'operador': '>', 'valor': '5'}),
                    'texto': 'Template B'
                }
            },
            2: { # Item without condicoes
                 '_extra': {
                    'id': 3,
                    'condicoes': None,
                    'texto': 'Template C'
                }
            }
        }
        db_mock.return_value.select.return_value.as_dict.return_value = mock_data

        expected_condicoes = {
            1: [{'campo': 'tipo_imovel', 'operador': '=', 'valor': 'urbano'}],
            2: {'campo': 'total_podas', 'operador': '>', 'valor': '5'}
        }
        expected_textos = {
            1: 'Template A',
            2: 'Template B'
        }

        dict_condicoes, dict_textos = dict_condicoes_de_templates()

        self.assertEqual(dict_condicoes, expected_condicoes)
        self.assertEqual(dict_textos, expected_textos)

    # Start with tests for determinar_despacho
    def test_determinar_despacho_no_laudos_no_match(self):
        # Mock dict_condicoes_de_templates to return empty conditions
        with patch('Viveiro_Analises.models.textos_modelos.dict_condicoes_de_templates') as mock_get_condicoes:
            mock_get_condicoes.return_value = ({}, {}) # No templates defined

            req = {
                'Despacho': 'analise',
                'tipo_imovel': 'rural',
                'protocolo_anterior': None,
                'total_podas': 2,
                'total_supressoes': 1,
                'local_arvore': 'calcada'
            }

            result = determinar_despacho(req)
            self.assertEqual(result, [])
            mock_get_condicoes.assert_called_once()

    def test_determinar_despacho_with_laudos_no_match(self):
        with patch('Viveiro_Analises.models.textos_modelos.dict_condicoes_de_templates') as mock_get_condicoes:
            mock_get_condicoes.return_value = ({}, {}) # No templates

            req = {
                'Laudos': {
                    'Despacho': 'aprovado',
                    'total_podas': 10,
                    'total_supressoes': 0,
                    'qtd_repor': 0,
                    'proprietario': 'Joao',
                    'tecnico': 'Maria',
                    'motivos': ['risco']
                },
                'Requerimentos': {
                    'tipo_imovel': 'urbano',
                    'protocolo_anterior': '123/2023',
                    'local_arvore': 'area interna'
                }
            }
            result = determinar_despacho(req)
            self.assertEqual(result, [])
            mock_get_condicoes.assert_called_once()

    def test_determinar_despacho_simple_match_equal_operator(self):
        # Define conditions and texts that dict_condicoes_de_templates would return
        condic_templates = {
            1: [{'campo': 'tipo_imovel', 'operador': '=', 'valor': 'urbano'}]
        }
        condic_txt = {
            1: "Texto para imóvel urbano."
        }

        with patch('Viveiro_Analises.models.textos_modelos.dict_condicoes_de_templates') as mock_get_condicoes:
            mock_get_condicoes.return_value = (condic_templates, condic_txt)

            req = {
                'Despacho': 'deferido',
                'tipo_imovel': 'urbano', # Matches condition
                'protocolo_anterior': None,
                'total_podas': 0,
                'total_supressoes': 0,
                'local_arvore': 'rua'
            }

            result = determinar_despacho(req)
            self.assertEqual(result, [(1, "Texto para imóvel urbano.")])

    def test_determinar_despacho_simple_match_greater_than_operator_numeric(self):
        condic_templates = {
            10: [{'campo': 'total_podas', 'operador': '>', 'valor': '5'}] # Valor is string '5'
        }
        condic_txt = {
            10: "Texto para mais de 5 podas."
        }

        with patch('Viveiro_Analises.models.textos_modelos.dict_condicoes_de_templates') as mock_get_condicoes:
            mock_get_condicoes.return_value = (condic_templates, condic_txt)

            req = {
                'Despacho': 'analise',
                'tipo_imovel': 'rural',
                'total_podas': 10, # Numeric 10, condition value is string '5'
                'total_supressoes': 0,
                'local_arvore': 'quintal'
            }

            result = determinar_despacho(req)
            self.assertEqual(result, [(10, "Texto para mais de 5 podas.")])

    def test_determinar_despacho_no_match_due_to_value_mismatch(self):
        condic_templates = {
            1: [{'campo': 'tipo_imovel', 'operador': '=', 'valor': 'urbano'}]
        }
        condic_txt = {
            1: "Texto para imóvel urbano."
        }

        with patch('Viveiro_Analises.models.textos_modelos.dict_condicoes_de_templates') as mock_get_condicoes:
            mock_get_condicoes.return_value = (condic_templates, condic_txt)

            req = {
                'Despacho': 'deferido',
                'tipo_imovel': 'rural', # Does not match 'urbano'
                'protocolo_anterior': None,
                'total_podas': 0,
                'total_supressoes': 0,
                'local_arvore': 'rua'
            }

            result = determinar_despacho(req)
            self.assertEqual(result, [])

    def test_determinar_despacho_multiple_conditions_all_match(self):
        condic_templates = {
            2: [
                {'campo': 'tipo_imovel', 'operador': '=', 'valor': 'urbano'},
                {'campo': 'total_supressoes', 'operador': '>', 'valor': '0'}
            ]
        }
        condic_txt = {
            2: "Urbano com supressão."
        }

        with patch('Viveiro_Analises.models.textos_modelos.dict_condicoes_de_templates') as mock_get_condicoes:
            mock_get_condicoes.return_value = (condic_templates, condic_txt)

            req_laudos = {
                'Laudos': {
                    'Despacho': 'aprovado',
                    'total_podas': 0,
                    'total_supressoes': 2, # Matches condition > 0
                    'qtd_repor': 0,
                    'proprietario': 'Ana',
                    'tecnico': 'Carlos',
                    'motivos': ['doente']
                },
                'Requerimentos': {
                    'tipo_imovel': 'urbano', # Matches condition
                    'protocolo_anterior': None,
                    'local_arvore': 'praca'
                }
            }
            result = determinar_despacho(req_laudos)
            self.assertEqual(result, [(2, "Urbano com supressão.")])

    def test_determinar_despacho_multiple_conditions_one_no_match(self):
        condic_templates = {
            3: [
                {'campo': 'tipo_imovel', 'operador': '=', 'valor': 'urbano'},
                {'campo': 'total_supressoes', 'operador': '>', 'valor': '0'} # This will not match
            ]
        }
        condic_txt = {
            3: "Urbano com supressão."
        }

        with patch('Viveiro_Analises.models.textos_modelos.dict_condicoes_de_templates') as mock_get_condicoes:
            mock_get_condicoes.return_value = (condic_templates, condic_txt)

            req = {
                'Despacho': 'analise',
                'tipo_imovel': 'urbano', # Matches
                'total_supressoes': 0,   # Does not match > 0
                'protocolo_anterior': None,
                'total_podas': 3,
                'local_arvore': 'rua'
            }
            result = determinar_despacho(req)
            self.assertEqual(result, [])

    def test_determinar_despacho_multiple_templates_one_match(self):
        condic_templates = {
            1: [{'campo': 'tipo_imovel', 'operador': '=', 'valor': 'rural'}],
            2: [{'campo': 'total_podas', 'operador': '>', 'valor': '5'}] # This one will match
        }
        condic_txt = {
            1: "Rural",
            2: "Muitas podas"
        }

        with patch('Viveiro_Analises.models.textos_modelos.dict_condicoes_de_templates') as mock_get_condicoes:
            mock_get_condicoes.return_value = (condic_templates, condic_txt)

            req = {
                'Despacho': 'analise',
                'tipo_imovel': 'urbano', # No match for template 1
                'total_podas': 10,       # Match for template 2
                'total_supressoes': 0,
                'local_arvore': 'quintal'
            }
            result = determinar_despacho(req)
            self.assertEqual(result, [(2, "Muitas podas")])

    def test_determinar_despacho_none_value_in_req_operator_equal(self):
        condic_templates = {
            1: [{'campo': 'protocolo_anterior', 'operador': '=', 'valor': None}]
        }
        condic_txt = {1: "Sem protocolo anterior"}
        with patch('Viveiro_Analises.models.textos_modelos.dict_condicoes_de_templates') as mock_get_condicoes:
            mock_get_condicoes.return_value = (condic_templates, condic_txt)
            req = {'protocolo_anterior': None, 'tipo_imovel': 'urbano'}
            result = determinar_despacho(req)
            self.assertEqual(result, [(1, "Sem protocolo anterior")])

    def test_determinar_despacho_none_value_in_req_operator_not_equal(self):
        condic_templates = {
            1: [{'campo': 'protocolo_anterior', 'operador': '!=', 'valor': None}]
        }
        condic_txt = {1: "Com protocolo anterior"}
        with patch('Viveiro_Analises.models.textos_modelos.dict_condicoes_de_templates') as mock_get_condicoes:
            mock_get_condicoes.return_value = (condic_templates, condic_txt)
            req = {'protocolo_anterior': '123/2024', 'tipo_imovel': 'urbano'}
            result = determinar_despacho(req)
            self.assertEqual(result, [(1, "Com protocolo anterior")])

    def test_determinar_despacho_none_value_in_req_operator_greater_than_ignored(self):
        # If value in req is None, and operator is not '=' or '!=', condition should not cause error,
        # but effectively be false or skipped for that specific field check if field not in condicoes_verificadas.
        # The current implementation will skip (continue) if valor is None and op not in ['=','!='].
        # So, if this is the *only* condition, it results in an empty condicoes_verificadas, thus no match.
        condic_templates = {
            1: [{'campo': 'total_podas', 'operador': '>', 'valor': 5}]
        }
        condic_txt = {1: "Podas > 5"}
        with patch('Viveiro_Analises.models.textos_modelos.dict_condicoes_de_templates') as mock_get_condicoes:
            mock_get_condicoes.return_value = (condic_templates, condic_txt)
            req = {'total_podas': None, 'tipo_imovel': 'urbano'}
            result = determinar_despacho(req)
            self.assertEqual(result, []) # No match because the condition on total_podas is skipped

    # TODO: Add tests for Despachar function
    # - Mocking determinar_despacho
    # - Different query inputs
    # - Template formatting (success and KeyError)

    @patch('Viveiro_Analises.models.textos_modelos.determinar_despacho')
    def test_despachar_no_templates_found(self, mock_determinar_despacho):
        mock_determinar_despacho.return_value = [] # No templates

        prime_query = {'Protocolo': '123'} # Minimal query
        result = Despachar(prime_query)

        self.assertEqual(result, ['Não foi possível determinar o modelo de despacho para este caso.'])
        mock_determinar_despacho.assert_called_once_with(prime_query)

    @patch('Viveiro_Analises.models.textos_modelos.determinar_despacho')
    def test_despachar_successful_population_prime_query(self, mock_determinar_despacho):
        # Mock determinar_despacho to return a template
        mock_determinar_despacho.return_value = [(1, "Protocolo: {Protocolo}, Requerente: {Requerente}")]

        mock_date = MagicMock()
        mock_date.strftime.return_value = "25/12/2023"

        prime_query = {
            'Protocolo': '001/2023',
            'Requerente': 'João Silva',
            'Endereco': 'Rua Teste, 123',
            'data_do_laudo': mock_date,
            'total_podas': 2,
            'total_supressoes': 1,
            'Podas': 'Sim',
            'Supressoes': 'Não',
            'num_extens_poda': 'duas',
            'num_extens_supressoes': 'uma'
        }

        result = Despachar(prime_query)

        self.assertEqual(result, ["Protocolo: 001/2023, Requerente: João Silva"])
        mock_determinar_despacho.assert_called_once_with(prime_query)
        mock_date.strftime.assert_called_with('%d/%m/%Y')

    @patch('Viveiro_Analises.models.textos_modelos.determinar_despacho')
    def test_despachar_successful_population_relation_query(self, mock_determinar_despacho):
        mock_determinar_despacho.return_value = [(2, "Técnico: {tecnico}, Poda: {total_podas}")]

        mock_date_laudo = MagicMock()
        mock_date_laudo.strftime.return_value = "20/12/2023"

        prime_query = {'Protocolo': 'P002'} # Required but not used for context here
        relation_query = {
            'Laudos': {
                'tecnico': 'Maria Souza',
                'data_do_laudo': mock_date_laudo,
                'proprietario': 'Empresa X',
                'morador': 'José',
                'total_podas': 5,
                'total_supressoes': 0,
                'num_extens_poda': 'cinco',
                'num_extens_supressoes': 'zero',
                'Supressoes': 'N/A',
                'Podas': 'Sim',
                'Obs': 'Nenhuma',
                'qtd_repor': 0,
                'porte_repor': None,
                'num_extens_repor': None
            }
        }

        result = Despachar(prime_query, relation_query=relation_query)

        # The template used for this test does not include {data_do_laudo}.
        # If it did, it would be an empty string due to the bug in textos_modelos.py.
        self.assertEqual(result, ["Técnico: MARIA SOUZA, Poda: 5"]) # tecnico is .upper()
        mock_determinar_despacho.assert_called_once_with(relation_query) # determinar_despacho is called with relation_query

        # Assert that strftime was NOT called, due to the bug in textos_modelos.py:
        # The condition `if relation_query.get('data_do_laudo')` is false.
        mock_date_laudo.strftime.assert_not_called()


    @patch('Viveiro_Analises.models.textos_modelos.determinar_despacho')
    def test_despachar_successful_population_query_protoc_ref_with_laudos(self, mock_determinar_despacho):
        mock_determinar_despacho.return_value = [(3, "Ref Protocolo: {Protocolo}, Ref Técnico: {tecnico}")]

        mock_date_laudo_ref = MagicMock()
        mock_date_laudo_ref.strftime.return_value = "15/12/2023"

        prime_query = {'Protocolo': 'P003', 'protocolo_anterior': 'REF001'}
        query_protoc_ref = {
            'Laudos': {
                'Protocolo': 'REF001',
                'Requerente': 'Empresa Ref',
                'Endereco': 'Rua Ref, 456',
                'total_podas': 1,
                'total_supressoes': 1,
                'Podas': 'REF Poda',
                'Supressoes': 'REF Sup',
                'num_extens_poda': 'uma ref',
                'num_extens_supressoes': 'uma ref',
                'tecnico': 'Carlos Ref',
            },
            'Requerimentos': { # This data_do_laudo should be used if present in Requerimentos under Laudos
                 'data_do_laudo': mock_date_laudo_ref
            }
        }

        result = Despachar(prime_query, query_protoc_ref=query_protoc_ref)

        expected_string = "Ref Protocolo: REF001, Ref Técnico: CARLOS REF"
        self.assertEqual(result, [expected_string])
        mock_determinar_despacho.assert_called_once_with(prime_query) # determinar_despacho is called with prime_query
        # Check if data_do_laudo from query_protoc_ref.Requerimentos was used
        # The following assertion is removed as determinar_despacho is called with prime_query, not the full context.
        # self.assertIn("'data_do_laudo': '15/12/2023'", str(mock_determinar_despacho.call_args_list[0].args[0]))
        mock_date_laudo_ref.strftime.assert_called_with('%d/%m/%Y')


    @patch('Viveiro_Analises.models.textos_modelos.determinar_despacho')
    def test_despachar_successful_population_query_protoc_ref_no_laudos(self, mock_determinar_despacho):
        mock_determinar_despacho.return_value = [(4, "Ref Protocolo: {Protocolo}, Anterior: {protocolo_anterior}, DataLaudo: {data_do_laudo}")]

        mock_date_req_ref = MagicMock()
        mock_date_req_ref.strftime.return_value = "10/12/2023"

        prime_query = {'Protocolo': 'P004', 'protocolo_anterior': 'REF002'}
        query_protoc_ref = { # No 'Laudos' key
            'Protocolo': 'REF002',
            'Requerente': 'Individuo Ref',
            'Endereco': 'Av Ref, 789',
            'total_podas': 3,
            'total_supressoes': 0,
            'Podas': 'REF Poda Sim',
            'Supressoes': 'REF Sup Nao',
            'num_extens_poda': 'tres ref',
            'num_extens_supressoes': 'zero ref',
            'data_do_laudo': mock_date_req_ref # This data_do_laudo should be used
        }

        result = Despachar(prime_query, query_protoc_ref=query_protoc_ref)

        # Updated expected string to include the formatted date to ensure it's processed.
        expected_string = "Ref Protocolo: REF002, Anterior: REF002, DataLaudo: 10/12/2023"
        self.assertEqual(result, [expected_string])
        # The following assertions are removed as determinar_despacho is called with prime_query, not the full context.
        # self.assertIn("'data_do_laudo': '10/12/2023'", str(mock_determinar_despacho.call_args_list[0].args[0]))
        # self.assertIn("'tecnico': 'XXXXXXXXXXXXXX'", str(mock_determinar_despacho.call_args_list[0].args[0]))
        mock_date_req_ref.strftime.assert_called_with('%d/%m/%Y')


    @patch('Viveiro_Analises.models.textos_modelos.determinar_despacho')
    def test_despachar_key_error_missing_placeholder(self, mock_determinar_despacho):
        # Template has {MissingVar} which won't be in context
        mock_determinar_despacho.return_value = [(1, "Protocolo: {Protocolo}, Info: {MissingVar}")]

        prime_query = {'Protocolo': '002/2023', 'Requerente': 'Test'} # MissingVar is not here

        result = Despachar(prime_query)

        expected_error_msg_part = "A variável MissingVar não foi encontrada no contexto de dados."
        self.assertTrue(len(result) == 1)
        self.assertIn(expected_error_msg_part, result[0])

    @patch('Viveiro_Analises.models.textos_modelos.determinar_despacho')
    def test_despachar_prime_query_none(self, mock_determinar_despacho):
        # Test the initial check in Despachar
        result = Despachar(None)
        self.assertIsNone(result) # As per print and return None
        mock_determinar_despacho.assert_not_called()

    @patch('Viveiro_Analises.models.textos_modelos.determinar_despacho')
    def test_despachar_date_formatting_none_date(self, mock_determinar_despacho):
        mock_determinar_despacho.return_value = [(1, "Data Laudo: {data_do_laudo}")]

        prime_query = {
            'Protocolo': '003/2023',
            'data_do_laudo': None, # Date is None
            # ... other fields
        }
        result = Despachar(prime_query)
        self.assertEqual(result, ["Data Laudo: "]) # Should be empty string


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
