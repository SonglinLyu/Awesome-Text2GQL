from antlr4 import CommonTokenStream, InputStream

from app.impl.iso_gql.grammar.GQLLexer import GQLLexer
from app.impl.iso_gql.grammar.GQLParser import GQLParser
from app.impl.tugraph_cypher.grammar.LcypherLexer import LcypherLexer
from app.impl.tugraph_cypher.grammar.LcypherParser import LcypherParser

from app.impl.iso_gql.translator.iso_gql_query_translator import (
    IsoGqlQueryTranslator as GQLTranslator,
)
from app.impl.tugraph_cypher.ast_visitor.tugraph_cypher_ast_visitor import TugraphCypherAstVisitor
from app.impl.tugraph_cypher.translator.tugraph_cypher_query_translator import (
    TugraphCypherQueryTranslator as CypherTranslator,
)

import re

# print a cypher AST
query_cypher = "MATCH (u:USER)-[:Approves]->(t:TRANSACTION) WITH u, COUNT(DISTINCT t) AS approved_transactions MATCH (u)-[:Approves]->(b:BUDGET) WITH u, approved_transactions, COUNT(DISTINCT b) AS approved_budgets MATCH (u)-[:Approves]->(r:REPORT) WITH u, approved_transactions, approved_budgets, COUNT(DISTINCT r) AS approved_reports WHERE approved_transactions >= 1 AND approved_budgets >= 1 AND approved_reports >= 1 RETURN u.user_id, u.role, u.department, approved_transactions + approved_budgets + approved_reports AS total_approved_items"

input_stream_cypher = InputStream(query_cypher)
lexer_cypher = LcypherLexer(input_stream_cypher)
token_stream_cypher = CommonTokenStream(lexer_cypher)
parser_cypher = LcypherParser(token_stream_cypher)
tree_cypher = parser_cypher.oC_Cypher()

print(f"[Cypher AST]:{tree_cypher.toStringTree(recog=parser_cypher)}")

query_visitor = TugraphCypherAstVisitor()
gql_translator = GQLTranslator()
cypher_translator = CypherTranslator()

musk_query = query_cypher
for word in gql_translator.get_reserved_worlds():
    musk_query = re.sub(r'\[:{}\]'.format(word), f'[:`{word}`]', musk_query, flags=re.IGNORECASE)
musk_query = musk_query.replace("CREATE", "INSERT")
print(musk_query)
if gql_translator.grammar_check(musk_query):
    print("CORRECT")


success, query_pattern = query_visitor.get_query_pattern(query_cypher)
if success:
    query_gql = gql_translator.translate(query_pattern)
    print(query_gql)
    if gql_translator.grammar_check(query_gql):
        print("CORRECT")
