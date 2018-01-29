from appEnrollment.api.serializers import PatientsSerializer

p = PatientsSerializer(data={
  "patients": [
    {
      "identifier": "bbb",
      "operator": "foo",
      "firstName": "Mario",
      "lastName": "Rossi",
      "fiscalCode": "MRIRSS",
      "birthDate": "1940-01-01",
      "birthPlace": "aa",
      "birthZipCode": "ss",
      "residencePlace": "dd",
      "residenceZipCode": "ss",
      "sex": "M",
      "race": "ss",
      "medicalCenter": "dd",
      "urlIC": "http://foo.com/IC/ICMarioRossi.pdf",
      "ICcode": "s",
      "project": "Funnel"
    },
    {
      "identifier": "aaa",
      "operator": "foo",
      "firstName": "Maria",
      "lastName": "Verde",
      "fiscalCode": "MRARSS",
      "birthDate": "1940-01-01",
      "birthPlace": "aa",
      "birthZipCode": "ss",
      "residencePlace": "dd",
      "residenceZipCode": "ss",
      "sex": "F",
      "race": "ss",
      "medicalCenter": "dd",
      "urlIC": "http://foo.com/IC/ICMarioRossi.pdf",
      "ICcode": "s",
      "project": "Funnel"
    }
  ]
}
)

p.is_valid()

p.save()

