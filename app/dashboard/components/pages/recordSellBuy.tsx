import { useEffect, useState } from "react";

export default function DisplayOrders() {
  const [orders, setOrders] = useState([]); // Store orders for a client
  const [allClients, setAllClients] = useState([]); // Store the full list of clients
  const [clients, setClients] = useState([]); // Store the filtered list of clients
  const [selectedClient, setSelectedClient] = useState(null); // Client for the pop-up
  const [responseMessage, setResponseMessage] = useState(""); // Message to display
  const [searchInput, setSearchInput] = useState({
    cus_id: "",
    cus_name: "",
    phone_number: "",  
  }); // Inputs for search
  const [showModal, setShowModal] = useState(false); // Modal visibility

  // Fetch all clients
  const fetchClients = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        setResponseMessage("You are not logged in. Please log in.");
        return;
      }

      const response = await fetch("http://127.0.0.1:8000/staff/client", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAllClients(data.result || []); // Store the full list
        setClients(data.result || []); // Initially display all clients
      } else {
        const errorData = await response.json();
        setResponseMessage(errorData.detail || "Error fetching clients.");
      }
    } catch (error) {
      console.error("Error fetching clients:", error);
      setResponseMessage("Failed to connect to the server.");
    }
  };

  // Fetch orders for a specific client
  const fetchOrders = async (cus_id) => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        setResponseMessage("You are not logged in. Please log in.");
        return;
      }

      const response = await fetch(
        `http://127.0.0.1:8000/staff/order?cus_id=${cus_id}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setOrders(data.result || []);
        setShowModal(true); // Show the modal
      } else {
        const errorData = await response.json();
        setResponseMessage(errorData.detail || "Error fetching orders.");
      }
    } catch (error) {
      console.error("Error fetching orders:", error);
      setResponseMessage("Failed to connect to the server.");
    }
  };

  // Handle client search
const handleClientSearch = () => {
  const { cus_id, cus_name, phone_number } = searchInput;

  // Reset the client list before filtering
  let filteredClients = [...allClients];

  if (cus_id || cus_name || phone_number) {
    filteredClients = allClients.filter((client) => {
      const matchId = cus_id && client.cus_id === parseInt(cus_id);
      const matchName =
        cus_name && client.cus_name.toLowerCase().includes(cus_name.toLowerCase());
      const matchPhone =
        phone_number &&
        client.phone_number.toLowerCase().includes(phone_number.toLowerCase());

      // Include client if any of the conditions match (OR logic)
      return matchId || matchName || matchPhone;
    });
  }

  setClients(filteredClients);
  setResponseMessage(
    filteredClients.length > 0 ? "" : "No clients found with the given input."
  );
};


  // Handle input change for search
  const handleInputChange = (e) => {
    setSearchInput({
      ...searchInput,
      [e.target.name]: e.target.value,
    });
  };

  // Fetch clients on component load
  useEffect(() => {
    fetchClients();
  }, []);

  return (
    <section id="display_orders" className="p-6">
      <div className="container mx-auto">
        <div className="w-full bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-bold mb-6">ទិញ &លក់: រុករកអតិថិជន</h2>

          {/* Search Input and Submit Button */}
          <div className="mb-4 flex gap-4">
            <input
              type="text"
              name="cus_id"
              value={searchInput.cus_id}
              onChange={handleInputChange}
              className="flex-1 border border-gray-300 p-2 rounded"
              placeholder="បញ្ចូលលេខសំគាល់អតិថិជន"
            />
            <input
              type="text"
              name="cus_name"
              value={searchInput.cus_name}
              onChange={handleInputChange}
              className="flex-1 border border-gray-300 p-2 rounded"
              placeholder="បញ្ចូលឈ្មោះអតិថិជន"
            />
            <input
              type="text"
              name="phone_number"
              value={searchInput.phone_number}
              onChange={handleInputChange}
              className="flex-1 border border-gray-300 p-2 rounded"
              placeholder="បញ្ចូលលេខទូរសព្ទអតិថិជន"
            />
            <button
              onClick={handleClientSearch}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              ស្វែងរក
            </button>
          </div>

          {/* Clients Table */}
          <h2 className="text-xl font-bold mt-8 mb-4">  </h2>
          {clients.length > 0 ? (
            <div className="overflow-y-auto max-h-[650px] border border-gray-300 rounded-lg">
              <table className="w-full border-collapse border border-gray-300 text-sm">
                <thead className="sticky top-0 bg-orange-500 text-white z-10">
                  <tr>
                    <th className="border border-gray-300 p-2">លេខសំគាល់</th>
                    <th className="border border-gray-300 p-2">ឈ្មោះអតិថិជន</th>
                    <th className="border border-gray-300 p-2">លេខទូរសព្ទ</th>
                    <th className="border border-gray-300 p-2">អាសយដ្ឋាន</th>
                    <th className="border border-gray-300 p-2">លម្អិត</th>
                  </tr>
                </thead>
                <tbody>
                  {clients.map((client) => (
                    <tr key={client.cus_id}>
                      <td className="border border-gray-300 p-2 text-center">
                        {client.cus_id}
                      </td>
                      <td className="border border-gray-300 p-2 text-center">
                        {client.cus_name}
                      </td>
                      <td className="border border-gray-300 p-2 text-center">
                        {client.phone_number}
                      </td>
                      <td className="border border-gray-300 p-2 text-center">
                        {client.address}
                      </td>
                      <td className="border border-gray-300 p-2 text-center">
                        <button
                          onClick={() => {
                            setSelectedClient(client); // Store the selected client
                            fetchOrders(client.cus_id); // Fetch orders for the client
                          }}
                          className="bg-gray-500 text-white px-2 py-1 rounded hover:bg-green-400"
                        >
                          មើលបន្ថែម
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-center text-gray-700 mt-4">{responseMessage}</p>
          )}

          {/* Modal for Orders */}
          {showModal && (
  <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
    <div className="bg-white p-6 rounded-lg shadow-lg w-3/4 max-h-[80vh] overflow-y-auto">
      <h2 className="text-xl font-bold mb-4">
        ព័ត៌មានអតិថិជន: {selectedClient?.cus_name}
      </h2>

      <div className="overflow-y-auto max-h-[60vh]">
        {orders.map((order, index) => (
          <div key={index} className="mb-4">
            <p className="font-bold">ប្រាក់កក់: {order.order_deposit}</p>
            <p className="font-bold">
              ថ្ងៃកក់: {new Date(order.order_date).toLocaleDateString()}
            </p>

            <h3 className="font-bold mt-4 mb-2">ផលិតផល:</h3>

            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-300 text-sm">
                <thead className="bg-orange-500 text-white">
                  <tr>
                    <th className="border border-gray-300 p-2">ឈ្មោះផលិតផល</th>
                    <th className="border border-gray-300 p-2">ទំងន់</th>
                    <th className="border border-gray-300 p-2">ចំនួន</th>
                    <th className="border border-gray-300 p-2">តំលៃលក់</th>
                    <th className="border border-gray-300 p-2">ឈ្នួល</th>
                    <th className="border border-gray-300 p-2">ប្រាក់កក់</th>
                    <th className="border border-gray-300 p-2">តំលៃទិញចូលវិញ</th>
                  </tr>
                </thead>
                <tbody>
                  {order.products.map((product, idx) => (
                    <tr key={`${order.order_id}-${idx}`}>
                      <td className="border border-gray-300 p-2 text-center">
                        {product.prod_name}
                      </td>
                      <td className="border border-gray-300 p-2 text-center">
                        {product.order_weight}
                      </td>
                      <td className="border border-gray-300 p-2 text-center">
                        {product.order_amount}
                      </td>
                      <td className="border border-gray-300 p-2 text-center">
                        {product.product_sell_price}
                      </td>
                      <td className="border border-gray-300 p-2 text-center">
                        {product.product_labor_cost}
                      </td>
                      <td className="border border-gray-300 p-2 text-center">
                        {order.order_deposit}
                      </td>
                      <td className="border border-gray-300 p-2 text-center">
                        {product.product_buy_price}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={() => setShowModal(false)} // Close the modal
        className="bg-red-500 text-white px-4 py-2 mt-4 rounded hover:bg-red-600"
      >
        បិទ
      </button>
    </div>
  </div>
)}

        </div>
      </div>
    </section>
  );
}
