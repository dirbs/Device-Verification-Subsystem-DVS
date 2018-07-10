from .responses import responses


class Pagination:

    @staticmethod
    def paginate(data, start, limit, imei, seen_with, url):  # TODO: optmizaion required
        try:
            count = len(data['associated_msisdn'])
            if count < start:
                return data

            # make response
            data['start'] = start
            data['limit'] = limit
            data['count'] = count

            # make URLs
            # make previous url
            if start == 1:
                data['previous'] = ''
            else:
                start_copy = max(1, start - limit)
                limit_copy = max(1, start - 1)
                data['previous'] = url + '?imei=%s&seen_with=%d&start=%d&limit=%d' % (
                    imei, seen_with, start_copy, limit_copy)

            # make next url
            if start + limit > count:
                data['next'] = ''
            else:
                start_copy = start + limit
                data['next'] = url + '?imei=%s&seen_with=%d&start=%d&limit=%d' % (imei, seen_with, start_copy, limit)

            # finally extract result according to bounds
            data['associated_msisdn'] = data['associated_msisdn'][
                                        (start - 1):(start - 1 + limit) if (start - 1 + limit) <= count else count]
            return data, responses.get('ok')

        except Exception as e:
            raise e
