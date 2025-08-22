import sys
sys.path.insert(0, '/Users/cmokashi/Documents/GitHub/neuroanalyst')

from app.models.process.logic.core import NeuProcessLogic, NeuProcessLogicArgument
from app.models.process.logic.code.python import encode_logic
from app.models.about import About

logic = NeuProcessLogic(
    about=About(
        name='test_func',
        description='Test function',
        version='1.0.0'
    ),
    language='python',
    code='''def test_func(input_filepath):
    return {'data': 'test'}''',
    import_statements=[],
    arguments=[]
)

result = encode_logic(logic)
print('Valid:', result.is_valid)
if not result.is_valid:
    print('Errors:', result.validation_errors)
else:
    print('Generated code works!')
    print('Code:')
    print(result.code)
