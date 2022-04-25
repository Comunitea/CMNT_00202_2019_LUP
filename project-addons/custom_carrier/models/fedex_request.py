from odoo.addons.delivery_fedex.models.fedex_request import FedexRequest

class FedexRequestEdit(FedexRequest):
    
    def process_shipment(self):
        TotalInsuredValue = self.client.factory.create('TotalInsuredValue')
        self.RequestedShipment.TotalInsuredValue = TotalInsuredValue
        self.RequestedShipment.TotalInsuredValue.Currency = self.RequestedShipment.PreferredCurrency
        self.RequestedShipment.TotalInsuredValue.Amount = self.RequestedShipment.CustomsClearanceDetail.CustomsValue.Amount
        return super(FedexRequest, self).process_shipment()
