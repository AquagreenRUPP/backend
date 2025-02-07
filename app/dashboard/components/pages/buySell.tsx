"use client";

import { useState, useEffect } from "react";

interface ProductDetail {
  prod_name: string;
  order_weight: string;
  order_amount: number;
  product_sell_price: number;
  product_labor_cost: number;
  product_buy_price: number;
}


export default function BuySellRecord() {
  const [cusName, setCusName] = useState("");
  const [address, setAddress] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [invoiceNumber, setInvoiceNumber] = useState("");
  const [orderDate, setOrderDate] = useState("");
  const [orderDeposit, setOrderDeposit] = useState<number>(0);
  const [lastOrderId, setLastOrderId] = useState<number | null>(null);
  const [orderProductDetail, setOrderProductDetail] = useState<ProductDetail[]>([
    {
      prod_name: "",
      order_weight: "",
      order_amount: 0,
      product_sell_price: 0,
      product_labor_cost: 0,
      product_buy_price: 0,
    },
  ]);
  const [responseMessage, setResponseMessage] = useState("");
  const [customerId, setCustomerId] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [nextClientId, setNextClientId] = useState("");

  // const [cusID, setCusID] = useState("");


  // Add a new product row
  const addProduct = () => {
    console.log("Adding a new product row");
    setOrderProductDetail((prev) => [
      ...prev,
      {
        prod_name: "",
        order_weight: "",
        order_amount: 0,
        product_sell_price: 0,
        product_labor_cost: 0,
        product_buy_price: 0,
      },
    ]);
  };
  
  const deleteRow = (index: number) => {
    setOrderProductDetail((prev) => prev.filter((_, i) => i !== index));
  };
  
  // Calculate Total Price
  const calculateTotalPrice = (): number => {
    return orderProductDetail.reduce((total, product) => {
      return total + product.product_labor_cost + product.order_amount * product.product_sell_price;
    }, 0);
  };

  // Cancel Order
  const cancelOrder = () => {
    // Clear all fields and reset
    setCustomerName("");
    setAddress("");
    setPhoneNumber("");
    setInvoiceNumber("");
    setOrderDate("");
    setOrderDeposit(0);
    fetchLastOrderId();
    // setOrderProductDetail([]);
    setResponseMessage("Order has been canceled.");
    setOrderProductDetail([
      {
        prod_name: "",
        order_weight: "",
        order_amount: 0,
        product_sell_price: 0,
        product_labor_cost: 0,
        product_buy_price: 0,
      },
    ]);
  };

  // Print Invoice
  const printInvoice = () => {
    // window.print();
    // setResponseMessage("Invoice is being printed.");
  };

  const handleSubmit = async () => {
    const idToSubmit = customerId.trim() || nextClientId;
  
    if (!idToSubmit || !customerName.trim() || !phoneNumber.trim() || !address.trim()) {
      setResponseMessage("Please fill in all required fields.");
      return;
    }

    if (
      orderProductDetail.length === 0 ||
      orderProductDetail.some(
        (product) =>
          !product.prod_name.trim() ||
          !product.order_weight.trim() ||
          product.order_amount <= 0 ||
          product.product_sell_price <= 0
      )
    ) {
      setResponseMessage("Please add at least one valid product with all fields filled.");
      return;
    }
  
    const payload = {
      cus_id: idToSubmit,
      cus_name: customerName,
      address: address,
      phone_number: phoneNumber,
      invoice_number: invoiceNumber || "N/A",
      order_date: orderDate || "N/A",
      order_deposit: orderDeposit,
      order_product_detail: orderProductDetail,
    };
  
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        setResponseMessage("Authentication failed. Please log in.");
        return;
      }
  
      const response = await fetch("http://127.0.0.1:8000/staff/order", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });
  
      if (response.ok) {
        const successData = await response.json();
        setResponseMessage(successData.message || "Order saved successfully!");
  
        // ✅ Ensure we fetch the latest Order ID **AFTER** the backend has updated
        setTimeout(async () => {
          await fetchLastOrderId(); // Delays fetching to allow database update
          await fetchNextClientId(); // Also update the customer ID
        }, 500); // 0.5 second delay to allow backend to update
  
        // ✅ Reset form fields
        setCustomerId("");
        setCustomerName("");
        setAddress("");
        setPhoneNumber("");
        setInvoiceNumber(""); // This will be updated when `fetchLastOrderId` runs
        setOrderDate("");
        setOrderDeposit(0);
        setOrderProductDetail([
          {
            prod_name: "",
            order_weight: "",
            order_amount: 0,
            product_sell_price: 0,
            product_labor_cost: 0,
            product_buy_price: 0,
          },
        ]);
      } else {
        const errorData = await response.json();
        setResponseMessage(errorData.message || "Failed to save order. Please try again.");
      }
    } catch (error) {
      setResponseMessage("Failed to connect to the server. Please check your connection.");
    }
  };
  
  
  

  useEffect(() => {
    if (orderProductDetail.length === 0) {
      addProduct(); 
    }
    fetchNextClientId();
    fetchLastOrderId();
  }, []);
  
  const updateProduct = (index: number, field: string, value: string | number) => {
    setOrderProductDetail((prev) =>
      prev.map((product, i) =>
        i === index
          ? {
              ...product,
              [field]: value || "",
              
            }
          : product
      )
    );
  };

  const fetchLastOrderId = async () => {
    try {
      console.log("Fetching last order ID...");
  
      const token = localStorage.getItem("access_token"); // Retrieve token
      if (!token) {
        console.error("No authentication token found. User may not be logged in.");
        return;
      }
  
      const response = await fetch("http://127.0.0.1:8000/staff/last-order-id", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,  // 🔹 Add Authorization header
        },
      });
  
      if (!response.ok) {
        console.error(`API request failed. Status: ${response.status}`);
        return;
      }
  
      const data = await response.json();
      console.log("API Response:", data);
  
      if (data?.result?.last_order_id !== undefined) {
        const nextId = data.result.last_order_id + 1;
        console.log("Setting lastOrderId:", nextId);
        setLastOrderId(nextId);
        setInvoiceNumber(`${nextId}`);
      } else {
        console.error("Unexpected API response format:", data);
      }
    } catch (error) {
      console.error("Error fetching last order ID:", error);
    }
  };
  
  
  const fetchNextClientId = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/staff/last-client_id", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });
  
      if (response.ok) {
        const data = await response.json();
        setNextClientId(data.result.id); // Use the id directly from the response
      } else {
        console.error("Failed to fetch next client ID");
      }
    } catch (error) {
      console.error("Error fetching next client ID:", error);
    }
  };
  

  return (
    <section id="buy_sell" className="p-6">
      <h1 className="text-2xl font-bold mb-6">កត់ត្រាការទិញ & លក់</h1>
      <div className="container mx-auto flex gap-6">
        {/* Left Section: Customer Information */}
        <div className="w-2/6 bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-bold mb-4">ព័ត៌មានអតិថិជន</h2>
          <div className="space-y-4">
          <div className="form-group">
            <label htmlFor="id" className="block text-gray-700 mb-2">
              លេខសំគាល់អតិថិជន:
            </label>
            <input
              type="number"
              id="id"
              value={customerId} // Controlled input
              onChange={(e) => setCustomerId(e.target.value)}
              className="w-full border border-gray-300 p-2 rounded"
              placeholder={nextClientId ? `${nextClientId}` : "Loading..."}

            />
          </div>

          <div className="form-group">
            <label htmlFor="customerName" className="block text-gray-700 mb-2">
              ឈ្មោះអតិថិជន:
            </label>
            <input
              type="text"
              id="customerName"
              value={customerName} // Use a separate state for Name
              onChange={(e) => setCustomerName(e.target.value)} // Update customerName state
              className="w-full border border-gray-300 p-2 rounded"
              placeholder="បញ្ចូលឈ្មោះអតិថិជន"
            />
          </div>


            <div className="form-group">
              <label htmlFor="phone" className="block text-gray-700 mb-2">
                លេខទូរស័ព្ទ:
              </label>
              <input
                type="text"
                id="phone"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                className="w-full border border-gray-300 p-2 rounded"
                placeholder="បញ្ចូលលេខទូរស័ព្ទ"
              />
            </div>
            <div className="form-group">
              <label htmlFor="address" className="block text-gray-700 mb-2">
                អាសយដ្ឋាន:
              </label>
              <input
                type="text"
                id="address"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                className="w-full border border-gray-300 p-2 rounded"
                placeholder="បញ្ចូលអាសយដ្ឋាន"
              />
            </div>
          </div>
        </div>

        {/* Right Section: Product Information */}
        <div className="flex-1 bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-bold mb-4">ព័ត៌មានផលិតផល</h2>
          <div className="form-group flex gap-4">
          {/* Invoice Number */}
          <div className="flex-1">
            <label htmlFor="invoiceNumber" className="block text-gray-700 mb-2">
              លេខវិក្កយបត្រ:
            </label>
            <input
              type="text"
              id="invoiceNumber"
              // value={invoiceNumber || `INV-${lastOrderId || "Loading..."}`}
              onChange={(e) => setInvoiceNumber(e.target.value)}
              className="w-full border border-gray-300 p-2 rounded"
              placeholder={invoiceNumber ? `${invoiceNumber}` : "Loading..."}
            />
          </div>
          {/* Order Date */}
          <div className="flex-1">
            <label htmlFor="orderDate" className="block text-gray-700 mb-2">
              ថ្ងៃបញ្ជាទិញ:
            </label>
            <input
              type="date"
              id="orderDate"
              value={orderDate}
              onChange={(e) => setOrderDate(e.target.value)}
              className="w-full border border-gray-300 p-2 rounded"
            />
          </div>
        </div>

        <div className="flex justify-center items-center h-20">
          <button
            onClick={addProduct}
            className="bg-gray-500 text-white py-2 px-4 rounded hover:bg-green-600"
          >
            បន្ថែមផលិតផល
          </button>
        </div>

          {/* <button
            onClick={removeProduct}
            className="bg-gray-500 text-white py-2 px-4 rounded hover:bg-red-600 mb-4"
          >
            លប់ចោលផលិតផល
          </button> */}
          <div className="w-full overflow-auto max-h-60 border border-gray-300 mt-4" 
     style={{ scrollbarGutter: "stable" }} // Ensures stable width even with a scrollbar
>
  <table className="w-full border-collapse border border-gray-300">
    <thead>
      <tr className="bg-orange-500 text-white">
        <th className="border border-gray-300 p-2">ឈ្មោះផលិតផល</th>
        <th className="border border-gray-300 p-2 w-24">ទំងន់</th> 
        <th className="border border-gray-300 p-2">ចំនួន</th>
        <th className="border border-gray-300 p-2">តំលៃលក់</th>
        <th className="border border-gray-300 p-2">ឈ្នួល</th>
        <th className="border border-gray-300 p-2">តំលៃទិញ</th>
        <th className="border border-gray-300 p-2"></th>
      </tr>
    </thead>
    <tbody>
      {orderProductDetail.map((product, index) => (
        <tr key={index}>
          <td className="border border-gray-300 p-2">
            <input
              type="text"
              value={product.prod_name}
              onChange={(e) => updateProduct(index, "prod_name", e.target.value)}
              className="w-full p-1 bg-transparent border-none focus:outline-none focus:ring-0"
              placeholder="ឈ្មោះ"
            />
          </td>
          {/* <td className="border border-gray-300 p-2 flex w-24">
           
            <input
              type="number"
              value={(product.order_weight || "").toString().replace(/\D/g, "0")} 
              onChange={(e) => {
                const numericPart = e.target.value.replace(/\D/g, ""); 
                const unitPart = (product.order_weight || "").toString().replace(/\d/g, "") || "";
                updateProduct(index, "order_weight", `${numericPart}${unitPart}`);
              }}
              className="w-2/4 p-1 bg-transparent border-none focus:outline-none focus:ring-0 text-right"
              placeholder="0"
            />
           
            <input
              type="text"
              value={(product.order_weight || "").toString().replace(/\d/g, "")} 
              onChange={(e) => {
                const unitPart = e.target.value.replace(/\d/g, "");
                const numericPart = (product.order_weight || "").toString().match(/\d+/)?.[0] || ""; 
                updateProduct(index, "order_weight", `${numericPart}${unitPart}`);
              }}
              className="w-2/4 p-1 bg-transparent border-none focus:outline-none focus:ring-0 text-left"
              placeholder=""
            />
          </td> */}

          <td className="border border-gray-300 p-2">
            <input
              type="text"
              value={product.order_weight}
              onChange={(e) => updateProduct(index, "order_weight", e.target.value)}
              className="w-full p-1 bg-transparent border-none focus:outline-none focus:ring-0 placeholder-gray-400 placeholder-opacity-50"
              placeholder="0"
            />
          </td>

          <td className="border border-gray-300 p-2">
              <input
                type="number"
                value={product.order_amount}
                onChange={(e) => updateProduct(index, "order_amount", parseInt(e.target.value))}
                className="w-full p-1 bg-transparent border-none focus:outline-none focus:ring-0 placeholder-gray-400 placeholder-opacity-50"
                placeholder="0" // Placeholder for order amount
              />
            </td>
            <td className="border border-gray-300 p-2">
              <input
                type="number"
                value={product.product_sell_price}
                onChange={(e) => updateProduct(index, "product_sell_price", parseFloat(e.target.value))}
                className="w-full p-1 bg-transparent border-none focus:outline-none focus:ring-0 placeholder-gray-400 placeholder-opacity-50"
                placeholder="0.00" // Placeholder for sell price
              />
            </td>
            <td className="border border-gray-300 p-2">
              <input
                type="number"
                value={product.product_labor_cost}
                onChange={(e) => updateProduct(index, "product_labor_cost", parseFloat(e.target.value))}
                className="w-full p-1 bg-transparent border-none focus:outline-none focus:ring-0 placeholder-gray-400 placeholder-opacity-50"
                placeholder="0.00" // Placeholder for labor cost
              />
            </td>
            <td className="border border-gray-300 p-2">
              <input
                type="number"
                value={product.product_buy_price}
                onChange={(e) => updateProduct(index, "product_buy_price", parseFloat(e.target.value))}
                className="w-full p-1 bg-transparent border-none focus:outline-none focus:ring-0 placeholder-gray-400 placeholder-opacity-50"
                placeholder="0.00" // Placeholder for buy price
              />
            </td>
          <td className="border border-gray-300 p-2">
            <button
              onClick={() => deleteRow(index)}
              className="bg-red-500 text-white py-1 px-3 rounded hover:bg-red-600"
            >
              លប់
            </button>
          </td>
        </tr>
      ))}
    </tbody>
  </table>
</div>

          <div className="form-group flex gap-4 mt-4">
  {/* Total Price */}
  <div className="flex-1">
    <label htmlFor="totalPrice" className="block text-gray-700 mb-2">
      តម្លៃសរុប:
    </label>
    <input
      type="number"
      id="totalPrice"
      value={calculateTotalPrice()}
      readOnly
      className="w-full border border-gray-300 p-2 rounded bg-gray-100"
    />
  </div>

  {/* Order Deposit */}
  <div className="flex-1">
    <label htmlFor="orderDeposit" className="block text-gray-700 mb-2">
      កក់/បង់សរុប:
    </label>
    <input
      type="number"
      id="orderDeposit"
      value={orderDeposit}
      onChange={(e) => setOrderDeposit(parseFloat(e.target.value))}
      className="w-full border border-gray-300 p-2 rounded"
    />
  </div>
</div>


<div className="flex justify-center gap-4 mt-6">
  <button
    onClick={handleSubmit}
    className="bg-gray-500 text-white py-2 px-6 rounded hover:bg-blue-600 shadow-md"
  >
    កត់ត្រាទុក
  </button>

  <button
    onClick={printInvoice}
    className="bg-gray-500 text-white py-2 px-6 rounded hover:bg-green-600 shadow-md"
  >
    បោះពុម្ពវិក្កយបត្រ
  </button>

  <button
    onClick={cancelOrder}
    className="bg-gray-500 text-white py-2 px-6 rounded hover:bg-red-600 shadow-md"
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
