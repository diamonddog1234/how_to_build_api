from flask import request, jsonify
from flask_restful import Resource

from core import get_database_session
from core.auth.jwt import check_role_validation, check_validation
from core.models import TubeSample


class AddSample(Resource):
    @check_role_validation(['ChangeRecord'])
    def post(self):
        json_data = request.get_json()
        if 'tubeId' not in json_data:
            return jsonify({'msg': 'no_tubeId'})
        if 'depth' not in json_data:
            return jsonify({'msg': 'no_depth'})
        if 'date' not in json_data:
            return jsonify({'msg': 'no_date'})
        if 'value' not in json_data:
            return jsonify({'msg': 'no_value'})

        value = float(json_data['value'])
        depth = float(json_data['depth'])
        tube_id = int(json_data['tubeId'])
        date = json_data['date']

        db_sample = get_database_session().query(TubeSample).\
            filter(TubeSample.tube_id == tube_id).\
            filter(TubeSample.date == date).first()
        if db_sample:
            return jsonify({'msg': 'NOT_ORIGINAL_SAMPLE'})
        sample = TubeSample(value = value, depth = depth, tube_id = tube_id, date = date)

        try:
            get_database_session().add(sample)
            get_database_session().commit()
        except:
            return jsonify({'msg': 'NO_TUBE'})
        return jsonify({'msg': 'OK', 'sample_id': sample.id})


class DeleteSample(Resource):
    @check_role_validation(['ChangeRecord'])
    def post(self):
        json_data = request.get_json()
        if 'sampleId' not in json_data:
            return jsonify({'msg': 'no_sampleId'})
        sample_id = int(json_data['sampleId'])
        db_sample = get_database_session().query(TubeSample).\
            filter(TubeSample.id == sample_id).\
            first()
        if not db_sample:
            return jsonify({'msg': 'NO_SAMPLE'})
        get_database_session().delete(db_sample)
        get_database_session().commit()
        return jsonify({'msg': 'OK'})


class ChangeSample(Resource):
    @check_role_validation(['ChangeRecord'])
    def post(self):
        json_data = request.get_json()
        if 'sampleId' not in json_data:
            return jsonify({'msg': 'no_sampleId'})
        sample_id = int(json_data['sampleId'])
        db_sample = get_database_session().query(TubeSample).\
            filter(TubeSample.id == sample_id).\
            first()
        if not db_sample:
            return jsonify({'msg': 'NO_SAMPLE'})
        old_sample = db_sample.to_basic_dictionary()
        new_value = db_sample.value
        new_tube_id = db_sample.tube_id
        new_depth = db_sample.depth
        new_date = db_sample.date
        if 'value' in json_data:
            new_value = float(json_data['value'])
        if 'depth' in json_data:
            new_depth = float(json_data['depth'])
        if 'tubeId' in json_data:
            new_tube_id = int(json_data['tubeId'])
        if 'date' in json_data:
            new_date = json_data['date']

        db_sample_repeat = get_database_session().query(TubeSample).\
            filter(TubeSample.date == new_date).\
            filter(TubeSample.tube_id == new_tube_id).\
            filter(TubeSample.id != sample_id).\
            first()
        if db_sample_repeat:
            return jsonify({'msg': 'NOT_ORIGINAL_SAMPLE'})
        try:
            db_sample.value = new_value
            db_sample.depth = new_depth
            db_sample.tube_id = new_tube_id
            db_sample.date = new_date
            get_database_session().commit()
        except:
            return jsonify({'msg': 'NO_TUBE'})
        return jsonify({'msg': 'OK'})


class GetSampleList(Resource):
    @check_validation
    def post(self):
        db_samples = get_database_session().query(TubeSample).all()
        return jsonify({'samples': [sample.to_basic_dictionary() for sample in db_samples]})



class GetSample(Resource):
    @check_validation
    def post(self, sample_id):
        db_sample = get_database_session().query(TubeSample).filter(TubeSample.id == sample_id).first()
        if not db_sample:
            return jsonify({'msg': 'NO_SAMPLE'})
        return jsonify(db_sample.to_basic_dictionary())
