<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:tei="http://www.tei-c.org/ns/1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output encoding="UTF-8" method="xml" />

  <!-- Keep only text that occurs within tei:l, unless the inverse
       parameter is true, in which case, keep only text that does not
       occur in tei:l. Keep as much structure as possible without
       having masses of empty elements. -->

  <xsl:param name="inverse" select="0" />

  <xsl:template match="tei:text">
    <xsl:copy>
      <xsl:apply-templates select="@*" />
      <xsl:choose>
        <xsl:when test="$inverse">
          <xsl:apply-templates mode="inverse" select="*" />
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates mode="verse" select="*" />
        </xsl:otherwise>
      </xsl:choose>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="tei:l" mode="verse">
    <xsl:copy-of select="." />
  </xsl:template>

  <xsl:template match="tei:lg//tei:lb" mode="verse">
    <xsl:copy-of select="." />
  </xsl:template>

  <xsl:template match="*" mode="verse">
    <xsl:if test=".//tei:l">
      <xsl:copy>
        <xsl:apply-templates mode="verse" select="@*|*" />
      </xsl:copy>
    </xsl:if>
  </xsl:template>

  <xsl:template match="@*" mode="verse">
    <xsl:copy />
  </xsl:template>

  <xsl:template match="text()" mode="verse" />

  <xsl:template match="tei:l" mode="inverse" />

  <xsl:template match="@*|node()" mode="inverse">
    <xsl:copy>
      <xsl:apply-templates mode="inverse" select="@*|node()" />
    </xsl:copy>
  </xsl:template>

  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()" />
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
