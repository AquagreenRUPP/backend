import React, { useState, useEffect } from "react";
// import { useState } from "react";

export default function RecordPawn() {
  // Initial form state
  const initialFormState = {
    cus_id: 0,
    cus_name: "",
    address: "",
    phone_number: "",
    pawn_deposit: 0,
    pawn_date: "",
    pawn_expire_date: "",
    pawn_product_detail: [
      {
        prod_name: "",
        pawn_weight: "",
        pawn_amount: 0,
        pawn_unit_price: 0,
      },
    ],
  };

  // Form state
  const [formData, setFormData] = useState(initialFormState);
  const [responseMessage, setResponseMessage] = useState("");
  const [nextPawnId, setNextPawnId] = useState("");
  const [nextClientId, setNextClientId] = useState("");

  // Handle input changes for main form fields
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const deleteRow = (index) => {
    setFormData((prev) => ({
      ...prev,
      pawn_product_detail: prev.pawn_product_detail.filter((_, i) => i !== index),
    }));
  };
  
  
  // Handle changes in product details
  const handleProductChange = (index, field, value) => {
    // Remove leading zeros from numeric inputs
    let newValue = value;
  
    if (typeof value === "string") {
      newValue = value.replace(/^0+/, ""); // Remove leading zeros
    }
  
    setFormData((prev) => ({
      ...prev,
      pawn_product_detail: prev.pawn_product_detail.map((product, i) =>
        i === index
          ? {
              ...product,
              [field]: field.includes("amount") || field.includes("price")
                ? Number(newValue) || "" // Ensure it's a number or empty string
                : newValue,
            }
          : product
      ),
    }));
  };
  

  // Add new product row
  const handleAddProduct = () => {
    setFormData((prev) => ({
      ...prev,
      pawn_product_detail: [
        ...prev.pawn_product_detail,
        {
          prod_name: "",
          pawn_weight: "",
          pawn_amount: 0,
          pawn_unit_price: 0,
        },
      ],
    }));
  };

  // Remove last product row
  const handleRemoveProduct = () => {
    if (formData.pawn_product_detail.length > 1) {
      setFormData((prev) => ({
        ...prev,
        pawn_product_detail: prev.pawn_product_detail.slice(0, -1),
      }));
    }
  };

  // Calculate total amount
  const calculateTotal = () => {
    return formData.pawn_product_detail.reduce(
      (sum, product) => sum + (Number(product.pawn_amount) * Number(product.pawn_unit_price) || 0),
      0
    );
  };
  
  const handleSubmit = async () => {
    try {
      const token = localStorage.getItem("access_token");
  
      const response = await fetch("http://127.0.0.1:8000/staff/pawn", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });
  
      if (response.status === 403) {
        setResponseMessage("Authentication error. Please log in again.");
        return;
      }
  
      if (!response.ok) {
        throw new Error("Failed to submit");
      }
  
      const result = await response.json();
      console.log("Success:", result);
  
      setResponseMessage("Successfully submitted!"); // Show success message
      handleReset(); // Reset the form
  
      // ✅ Fetch updated client and pawn IDs after submission
      await Promise.all([fetchNextClientId(), fetchNextPawnId()]);
  
    } catch (error) {
      console.error("Error:", error);
      setResponseMessage(`Failed to submit data: ${error.message}`);
    }
  };
  
  

  const fetchNextPawnId = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch("http://127.0.0.1:8000/staff/next-pawn-id", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });
  
      if (response.ok) {
        const data = await response.json();
        setNextPawnId(data.result.next_pawn_id);
        console.log("Updated Next Pawn ID:", data.result.next_pawn_id);
      } else {
        console.error("Failed to fetch next pawn ID");
      }
    } catch (error) {
      console.error("Error fetching next pawn ID:", error);
    }
  };
  

  const fetchNextClientId = async () => {
    try {
      const token = localStorage.getItem("access_token");
  
      const response = await fetch("http://127.0.0.1:8000/staff/last-client_id", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });
  
      if (!response.ok) {
        throw new Error("Failed to fetch next client ID");
      }
  
      const data = await response.json();
  
      if (data?.result?.id) {
        setNextClientId(data.result.id); // ✅ Update next client ID
        console.log("Updated Next Client ID:", data.result.id);
      } else {
        throw new Error("Invalid response format");
      }
    } catch (error) {
      console.error("Error fetching next client ID:", error);
    }
  };
  

  // Fetch pawn ID when component loads
  useEffect(() => {
    fetchNextPawnId();
    fetchNextClientId();
  }, []);

  // Reset form
  const handleReset = () => {
    setFormData(initialFormState);
  };

  return (
    <section id="record_pawn" className="p-6">
      <div className="container mx-auto flex flex-wrap gap-6">
        {/* Left Section */}
        <div className="w-2/5 bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-bold mb-4">ព័ត៌មានអតិថិជន</h2>
          <div className="space-y-4">
            <div className="form-group">
              <label htmlFor="customerID" className="block text-gray-700 mb-2">
                លេខសំគាល់:
              </label>
              <input
                type="text"
                value={nextClientId}
                readOnly
                className="w-full border border-gray-300 p-2 rounded bg-gray-50"
              />
            </div>
            <div className="form-group">
              <label htmlFor="cus_name" className="block text-gray-700 mb-2">
                ឈ្មោះ:
              </label>
              <input
                type="text"
                name="cus_name"
                value={formData.cus_name}
                onChange={handleInputChange}
                className="w-full border border-gray-300 p-2 rounded"
              />
            </div>
            <div className="form-group">
              <label htmlFor="phone_number" className="block text-gray-700 mb-2">
                លេខទូរសព្ទ:
              </label>
              <input
                type="text"
                name="phone_number"
                value={formData.phone_number}
                onChange={handleInputChange}
                className="w-full border border-gray-300 p-2 rounded"
              />
            </div>
            <div className="form-group">
              <label htmlFor="address" className="block text-gray-700 mb-2">
                អាសយដ្ឋាន:
              </label>
              <input
                type="text"
                name="address"
                value={formData.address}
                onChange={handleInputChange}
                className="w-full border border-gray-300 p-2 rounded"
              />
            </div>
          </div>
        </div>

        {/* Right Section */}
        <div className="w-3/5 flex-1 bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-bold mb-4">ព័ត៌មានផលិតផល</h2>
          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="form-group">
                <label htmlFor="orderpawnID" className="block text-gray-700 mb-2">
                  លេខវិក្កយបត្រ:
                </label>
                <input
                  type="text"
                  value={nextPawnId}
                  readOnly
                  className="w-full border border-gray-300 p-2 rounded bg-gray-50"
                />
              </div>
              {/* <div className="form-group">
                <label htmlFor="date" className="block text-gray-700 mb-2">
                  កាលបរិច្ឆេទ:
                </label>
                <input
                  type="date"
                  name="pawn_date"
                  value={formData.pawn_date}
                  onChange={handleInputChange}
                  className="w-full border border-gray-300 p-2 rounded"
                />
              </div> */}
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="form-group">
                <label htmlFor="checkin" className="block text-gray-700 mb-2">
                  ថ្ងៃបញ្ចាំ:
                </label>
                <input
                  type="date"
                  name="pawn_date"
                  value={formData.pawn_date}
                  onChange={handleInputChange}
                  className="w-full border border-gray-300 p-2 rounded"
                />
              </div>
              <div className="form-group">
                <label htmlFor="checkout" className="block text-gray-700 mb-2">
                  ថ្ងៃផុតកំណត់:
                </label>
                <input
                  type="date"
                  name="pawn_expire_date"
                  value={formData.pawn_expire_date}
                  onChange={handleInputChange}
                  className="w-full border border-gray-300 p-2 rounded"
                />
              </div>
            </div>
          </div>

          {/* Button Row */}
          <div className="flex justify-center gap-4 mt-4">
            <button
              type="button"
              onClick={handleAddProduct}
              className="bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600"
            >
              បន្ថែមផលិតផល
            </button>
            {/* <button
              type="button"
              onClick={handleRemoveProduct}
              className="bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600"
              disabled={formData.pawn_product_detail.length <= 1}
            >
              លប់ចោលផលិតផល
            </button> */}
          </div>

          {/* Table */}
          <div className="w-full overflow-auto max-h-60 border border-gray-300 mt-4"
          style={{ scrollbarGutter: "stable" }}
          >
  <table className="w-full border-collapse">
    <thead className="sticky top-0 bg-orange-500 text-white">
      <tr>
        <th className="border border-gray-300 p-2">ឈ្មោះ</th>
        <th className="border border-gray-300 p-2">ទំងន់</th>
        <th className="border border-gray-300 p-2">តំលៃបញ្ចាំ</th>
        <th className="border border-gray-300 p-2">ចំនួន</th>
        <th className="border border-gray-300 p-2"></th>
      </tr>
    </thead>
    <tbody>
      {formData.pawn_product_detail.map((product, index) => (
        <tr key={index} className="bg-white">
          <td className="border border-gray-300 p-2">
            <input
              type="text"
              value={product.prod_name}
              onChange={(e) => handleProductChange(index, "prod_name", e.target.value)}
              className="w-full p-1 bg-transparent border-none focus:outline-none focus:ring-0"
              placeholder="ឈ្មោះ"
            />
          </td>
          <td className="border border-gray-300 p-2">
            <input
              type="text"
              value={product.pawn_weight}
              onChange={(e) => handleProductChange(index, "pawn_weight", e.target.value)}
              className="w-full p-1 bg-transparent border-none focus:outline-none focus:ring-0"
              placeholder="0"
            />
          </td>
          <td className="border border-gray-300 p-2">
            <input
              type="number"
              value={product.pawn_amount}
              onChange={(e) => handleProductChange(index, "pawn_amount", e.target.value)}
              className="w-full p-1 bg-transparent border-none focus:outline-none focus:ring-0"
            />
          </td>
          <td className="border border-gray-300 p-2">
            <input
              type="number"
              value={product.pawn_unit_price}
              onChange={(e) => handleProductChange(index, "pawn_unit_price", e.target.value)}
              className="w-full p-1 bg-transparent border-none focus:outline-none focus:ring-0"
            />
          </td>
          <td className="border border-gray-300 p-2 text-center">
            <button
              onClick={() => deleteRow(index)}
              className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
            >
              លុប
            </button>
          </td>
        </tr>
      ))}
    </tbody>
  </table>
</div>


          {/* Summary Section */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
            <div className="form-group">
              <label htmlFor="totalAmount" className="block text-gray-700 mb-2">
                តំលៃសរុប:
              </label>
              <input
                type="number"
                readOnly
                value={calculateTotal()}
                className="w-full border border-gray-300 p-2 rounded bg-gray-50"
              />
            </div>
            <div className="form-group">
              <label htmlFor="pawn_deposit" className="block text-gray-700 mb-2">
                កក់/បង់សរុប:
              </label>
              <input
                type="number"
                name="pawn_deposit"
                value={formData.pawn_deposit}
                onChange={handleInputChange}
                className="w-full border border-gray-300 p-2 rounded"
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-center gap-4 mt-4">
            <button
              type="button"
              onClick={handleSubmit}
              className="bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600"
            >
              កត់ត្រាទុក
            </button>
            <button
              type="button"
              className="bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600"
            >
              បោះពុម្ពវិក្កយបត្រ
            </button>
            <button
              type="button"
              onClick={handleReset}
              className="bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600"
            >
              លប់ចោល
            </button>
          </div>
        </div>
      </div>
      {responseMessage && (
        <div className="mt-4 p-4 bg-gray-100 border border-gray-300 rounded">
          <p>{responseMessage}</p>
        </div>
      )}

    </section>
  );
}