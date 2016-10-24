import pytest

from normalise.tagger import tagify

test_list = [({0: "Hello"}),
             ({1: "1234"}),
             ({2: "this-splits"}),
             ({3: "!!MSC!?!"}),
             ({4: "'Help.'"}),
             ({5: "Skeiw's"}),
             ({6: "Ba'la'lwe'kew'hi."}),
             ({7: "123's"}),
             ({8: "123,000PYG"}),
             ({9: "222nd's"}),
             ({10: "100,000US$"}),
             ({11: "£20,000.35"}),
             ({12: '30°26\'46"'}),
             ({13: "SplitToken"}),
             ({14: "fish/chips"}),
             ({15: "Different—dashes"}),
             ({16: "Diff'ent-things's"}),
             ({17: "Sp°g"})
             ]

result_list = [({0: ("Hello", "ALPHA")}),
               ({1: ("1234", "NUMB")}),
               ({2: ("this-splits", "SPLT")}),
               ({3: ("!!MSC!?!", "MISC")}),
               ({4: ("'Help.'", "ALPHA")}),
               ({5: ("Skeiw's", "ALPHA")}),
               ({6: ("Ba'la'lwe'kew'hi.", "ALPHA")}),
               ({7: ("123's", "NUMB")}),
               ({8: ("123,000PYG", "NUMB")}),
               ({9: ("222nd's", "NUMB")}),
               ({10: ("100,000US$", "NUMB")}),
               ({11: ("£20,000.35", "NUMB")}),
               ({12: ('30°26\'46"', "NUMB")}),
               ({13: ("SplitToken", "SPLT")}),
               ({14: ("fish/chips", "SPLT")}),
               ({15: ("Different—dashes", "SPLT")}),
               ({16: ("Diff'ent-things's", "SPLT")}),
               ({17: ("Sp°g", "MISC")})
               ]
tagify_tests = zip(test_list, result_list)


@pytest.mark.parametrize(("test", "result"), tagify_tests)
def test_tagify(test, result):
    assert tagify(test) == result
