"""Event-row binding regression contract, independent from cryptographic digest validity."""
import uuid

DOMAINS = [('pricing','PriceEvent'),('quotation','QuotationEvent'),('sales','SaleEvent'),('payment','PaymentEvent'),('landing','LandingEvent'),('capture','CaptureEvent'),('library','LibraryEvent'),('opportunity','OpportunityEvent')]

class EventBindingCases:
    def event_data(self):
        rid, item = str(uuid.uuid4()), str(uuid.uuid4())
        key = 'opportunity_id' if self.domain == 'opportunity' else 'item_id'
        doc = {'id':rid,'scope':self.base.scope,key:item,'actor':'synthetic-actor','operation':'SYNTHETIC','data':{}}
        doc['event_digest'] = self.digest(doc)
        return rid,item,doc

    def rejects(self, call):
        with self.assertRaises(self.error) as error:
            call()
        self.assertEqual(error.exception.status,503)

    def test_receipt_rejects_valid_document_routed_by_corrupt_indices(self):
        rid,item,doc=self.event_data();self.insert(rid,item,doc)
        self.assertEqual(self.store.event(rid),doc)
        for field,value in [('id',str(uuid.uuid4())),('scope','foreign-scope'),(self.item_field,str(uuid.uuid4()))]:
            with self.subTest(field=field):
                original=rid if field=='id' else self.base.scope if field=='scope' else item
                self.update(rid,**{field:value})
                self.rejects(lambda:self.store.event(value if field=='id' else rid))
                self.update(value if field=='id' else rid,**{field:original})
                self.assertEqual(self.store.event(rid),doc)
        self.update(rid,document=['invalid-document']);self.rejects(lambda:self.store.event(rid))
        self.update(rid,document=doc)
        self.assertEqual(doc['event_digest'],self.digest({k:v for k,v in doc.items() if k!='event_digest'}))

    def test_history_cannot_reassign_a_valid_event_to_another_item(self):
        rid,item,doc=self.event_data();self.insert(rid,item,doc)
        wrong=str(uuid.uuid4());self.update(rid,**{self.item_field:wrong})
        self.rejects(lambda:self.store.last_event(wrong))
        self.rejects(lambda:list(self.store.events(wrong)))
        self.update(rid,**{self.item_field:item})
        self.assertEqual(self.store.last_event(item),doc)
        self.assertEqual(list(self.store.events(item)),[doc])

    def test_append_rejects_another_company_without_writing_an_event(self):
        rid,item,doc=self.event_data();doc['scope']='foreign-scope'
        doc['event_digest']=self.digest({k:v for k,v in doc.items() if k!='event_digest'})
        self.rejects(lambda:self.store.append(doc))
        self.assertIsNone(self.store.event(rid))
