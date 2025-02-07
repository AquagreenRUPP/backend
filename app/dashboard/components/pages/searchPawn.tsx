"use client";

import { useState, useEffect } from "react";

export default function SearchPawn() {
  const [searchParams, setSearchParams] = useState({
    cus_id: "",
    cus_name: "",
    phone_number: "",
  });
  const [searchResults, setSearchResults] = useState([]);
  const [selectedPawn, setSelectedPawn] = useState(null);
  const [showPopup, setShowPopup] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchAllPawns();
  }, []);

  const fetchAllPawns = async () => {
    setLoading(true);
    setError("");

    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch("http://127.0.0.1:8000/staff/pawns", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();
      console.log("All Pawns Data:", data);

      if (response.ok && data.result.length > 0) {
        setSearchResults(data.result);
      } else {
        setError("No records found.");
        setSearchResults([]);
      }
    } catch (err) {
      console.error("Fetch Error:", err);
      setError("Failed to fetch data.");
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    setLoading(true);
    setError("");

    try {
      const token = localStorage.getItem("access_token");

      const queryParams = new URLSearchParams();
      if (searchParams.cus_id) queryParams.append("cus_id", searchParams.cus_id);
      if (searchParams.cus_name) queryParams.append("cus_name", searchParams.cus_name);
      if (searchParams.phone_number) queryParams.append("phone_number", searchParams.phone_number);

      let apiUrl = "http://127.0.0.1:8000/staff/pawns";
      if (queryParams.toString()) {
        apiUrl += `?${queryParams.toString()}`;
      }

      console.log("API Request URL:", apiUrl);

      const response = await fetch(apiUrl, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();
      console.log("Search Response:", data);

      if (response.ok && data.result.length > 0) {
        setSearchResults(data.result);
      } else {
        setError("No results found.");
        setSearchResults([]);
      }
    } catch (err) {
      console.error("Search Error:", err);
      setError("Failed to fetch data.");
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setSearchParams((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const openDetailsPopup = (pawn) => {
    setSelectedPawn(pawn);
    setShowPopup(true);
  };

  return (
    <section id="search_pawn" className="p-6">
      <div className="container mx-auto flex flex-wrap gap-6">
        <div className="w-full bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-bold mb-4">ការរុករកព័ត៌មានអតិថិជនបញ្ចាំ</h2>

          {/* Search Inputs */}
          <div className="mb-4 flex gap-4">
  {/* Input Fields */}
  <input
    type="text"
    name="cus_id"
    placeholder="លេខសំគាល់អតិថិជន"
    value={searchParams.cus_id}
    onChange={handleInputChange}
    className="flex-1 border border-gray-300 p-2 rounded"
  />
  <input
    type="text"
    name="cus_name"
    placeholder="ឈ្មោះអតិថិជន"
    value={searchParams.cus_name}
    onChange={handleInputChange}
    className="flex-1 border border-gray-300 p-2 rounded"
  />
  <input
    type="text"
    name="phone_number"
    placeholder="លេខទូរស័ព្ទ"
    value={searchParams.phone_number}
    onChange={handleInputChange}
    className="flex-1 border border-gray-300 p-2 rounded"
  />

  {/* Search Button */}
  <button
    onClick={handleSearch}
    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
  >
    ស្វែងរក
  </button>
</div>


          {/* Error Message */}
          {error && <p className="text-red-500 mt-4">{error}</p>}

          {/* Results Table */}
          <div className="overflow-y-auto max-h-[650px] border border-gray-300 rounded-lg">
            <table className="w-full border-collapse border border-gray-300">
              <thead>
                <tr className="bg-orange-500 text-white">
                  <th className="border border-gray-300 p-2">លេខសំគាល់អតិថិជន</th>
                  <th className="border border-gray-300 p-2">ឈ្មោះ</th>
                  <th className="border border-gray-300 p-2">លេខទូរស័ព្ទ</th>
                  <th className="border border-gray-300 p-2">អាសយដ្ឋាន</th>
                  <th className="border border-gray-300 p-2">លម្អិត</th>
                </tr>
              </thead>
              <tbody>
                {searchResults.length > 0 ? (
                  searchResults.map((pawn, index) => (
                    <tr key={index} className="bg-white">
                      <td className="border border-gray-300 p-2">{pawn.cus_id}</td>
                      <td className="border border-gray-300 p-2">{pawn.customer_name}</td>
                      <td className="border border-gray-300 p-2">{pawn.phone_number}</td>
                      <td className="border border-gray-300 p-2">{pawn.address || "N/A"}</td>
                      <td className="border border-gray-300 p-2 text-center">
                        <button
                          onClick={() => openDetailsPopup(pawn)}
                          className="bg-gray-500 text-white px-2 py-1 rounded hover:bg-green-400"
                        >
                          មើលបន្ថែម
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="5" className="text-center py-4">គ្មានទិន្នន័យ</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Details Popup */}
      {/* Details Popup */}
{showPopup && selectedPawn && (
  <div className="fixed top-0 left-0 w-full h-full flex items-center justify-center bg-black bg-opacity-50">
    <div className="bg-white p-6 rounded-lg shadow-md max-w-4xl w-full">
      <h2 className="text-xl font-bold mb-4">ព័ត៌មានអំពីការបញ្ចាំ</h2>

      {/* Pawn Info */}
      <div className="mb-4">
        <p className="text-lg"><strong>ប្រាក់កក់:</strong> {selectedPawn.pawn_deposit} USD</p>
        <p className="text-lg"><strong>ថ្ងៃបញ្ចាំ:</strong> {selectedPawn.pawn_date?.split("T")[0]}</p>
        <p className="text-lg"><strong>ថ្ងៃផុតកំណត់:</strong> {selectedPawn.pawn_expire_date?.split("T")[0]}</p>
      </div>

      {/* Products Table */}
      <h3 className="text-lg font-semibold mt-4 mb-2">ផលិតផល</h3>
      <div className="overflow-x-auto max-h-72 border border-gray-300 rounded">
        <table className="w-full border-collapse border border-gray-300">
          <thead>
            <tr className="bg-orange-500 text-white">
              <th className="border border-gray-300 p-2">លេខសំគាល់ផលិតផល</th>
              <th className="border border-gray-300 p-2">ឈ្មោះផលិតផល</th>
              <th className="border border-gray-300 p-2">ទំងន់</th>
              <th className="border border-gray-300 p-2">ចំនួន</th>
              <th className="border border-gray-300 p-2">តម្លៃលក់</th>
            </tr>
          </thead>
          <tbody>
            {selectedPawn.products.map((product, index) => (
              <tr key={index} className="bg-white">
                <td className="border border-gray-300 p-2">{product.prod_id}</td>
                <td className="border border-gray-300 p-2">{product.prod_name}</td>
                <td className="border border-gray-300 p-2">{product.pawn_weight}</td>
                <td className="border border-gray-300 p-2">{product.pawn_amount}</td>
                <td className="border border-gray-300 p-2">{product.pawn_unit_price}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Close Button */}
      <div className="flex justify-left mt-4">
        <button
          onClick={() => setShowPopup(false)}
          className="bg-red-500 text-white px-4 py-2 mt-4 rounded hover:bg-red-600"
        >
          បិទ
        </button>
      </div>
    </div>
  </div>
)}

    </section>
  );
}
