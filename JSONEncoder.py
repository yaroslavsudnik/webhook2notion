from notion.collection import TableQueryResult

import app


class JSONEncoder(app.json_encoder):
    def default(self, o):
        if isinstance(o, TableQueryResult):
            result = {}
            for row in o:
                result.update({
                    row.title: {
                        'id': row.id,
                        'title': row.title
                    }
                })
            return result
        else:
            return super().default(o)
